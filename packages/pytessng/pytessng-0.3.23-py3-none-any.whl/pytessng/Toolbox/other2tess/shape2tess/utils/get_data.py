import os
import traceback
import collections
from datetime import datetime
import numpy as np
import shapefile
import dbfread
import scipy.spatial as spt
from pyproj import Proj
from .config import default_lane_width, min_width, join_point_distance
from .config import threshold_length, threshold_distance_max, threshold_distance_min
from .functions import calculate_center, generate_random_string
from .functions import calculate_lanes_with_same_points, calculate_laneNumber_list, line2surface
from .....Tessng.MyMenu import Logger
from .....Tessng.MyMenu import ProgressDialog as pgd


# 获取路段信息
def get_links_info(folder_path, is_use_lon_and_lat, is_use_center_line, laneFileName="lane", proj_mode=None):
    # 文件路径
    filePath_dbf_lane = os.path.join(folder_path, f"{laneFileName}.dbf")
    filePath_shp_lane = os.path.join(folder_path, f"{laneFileName}.shp")
    
    if not os.path.exists(filePath_dbf_lane) or not os.path.exists(filePath_shp_lane):
        raise Exception("Some files are missing !")
    
    # 读取文件
    try:
        all_data_dbf_lane = list(dbfread.DBF(filePath_dbf_lane, encoding='utf-8'))
        all_data_shp_lane = shapefile.Reader(filePath_shp_lane, encoding='utf-8').shapes()
    except:
        all_data_dbf_lane = list(dbfread.DBF(filePath_dbf_lane, encoding='gbk'))
        all_data_shp_lane = shapefile.Reader(filePath_shp_lane, encoding='gbk').shapes()
    
    # 寻找中心位置
    lon_list, lat_list = [], []
    for lane_data_shp in all_data_shp_lane:
        lon_list.extend([point[0] for point in lane_data_shp.points])
        lat_list.extend([point[1] for point in lane_data_shp.points])
    if is_use_lon_and_lat:
        lon_0, lat_0 = calculate_center(min(lat_list), max(lat_list), min(lon_list), max(lon_list))
    else:
        lon_0 = (min(lon_list) + max(lon_list)) / 2
        lat_0 = (min(lat_list) + max(lat_list)) / 2

    global p
    other_info = {
        "data_source": "Shape",
        "created_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if is_use_lon_and_lat:
        if "prj" in proj_mode:
            filePath_prj = os.path.join(folder_path, f"{laneFileName}.prj")
            proj_string = open(filePath_prj, "r").read()
        elif "tmerc" in proj_mode:
            proj_string = f'+proj=tmerc +lon_0={lon_0} +lat_0={lat_0} +ellps=WGS84'
        elif "utm" in proj_mode:
            proj_string = f'+proj=utm +zone={lon_0 // 6 + 31} +ellps=WGS84'
        elif "web" in proj_mode:
            proj_string = 'EPSG:3857'
        else:
            proj_string = f'+proj=tmerc +lon_0={lon_0} +lat_0={lat_0} +ellps=WGS84'
            Logger.logger_network.warning("No this projection mode!")
        p = Proj(proj_string)
        other_info["proj_string"] = proj_string
    else:
        p = lambda x, y: (x, y)
    
    x_center, y_center = p(lon_0, lat_0)
    x_move, y_move = -float(round(x_center, 3)), -float(round(y_center, 3))
    other_info["move_distance"] = {"x_move": x_move, "y_move": y_move}

    # 保存路段信息
    links_info = collections.defaultdict(lambda: {'lanes_data': {}, 'obj': None})
    # 保存车道信息
    lanes_info = {}
    # 读取数据，并组合dbf数据和shp数据
    for index, lane_data_shp in pgd.progress(enumerate(all_data_shp_lane), "数据读取中（1/8）"):
        # 获取该路段的dbf数据
        lane_data_dbf = all_data_dbf_lane[index]
        
        # 经纬度转为平面坐标
        xy_list = [p(point[0], point[1]) for point in lane_data_shp.points]
        
        # 判断属性z是否存在
        if hasattr(lane_data_shp, "z"):
            z_list = lane_data_shp.z
        else:
            z_list = [0 for _ in range(len(xy_list))]
        
        # 获取三维坐标
        points_3D = [[x, y, z] for (x, y), z in zip(xy_list, z_list)]
        
        # 记录link车道级信息, 两种关系，路段-车道 和 车道-路段
        road_id = lane_data_dbf.get('roadId')

        # 如果没有路段ID就跳过
        if not road_id:
            Logger.logger_network.warning("The roadId is missing!")
            continue

        # 车道ID用生成的随机字符串
        lane_id = lane_data_dbf.get('id') or generate_random_string()
        
        lane_type = lane_data_dbf.get('type') or "driving"
        lane_width = lane_data_dbf.get('width') or default_lane_width[lane_type]

        links_info[road_id]["lanes_data"][lane_id] = {
            'roadId': road_id,
            'type': lane_type,
            'width': lane_width,
            'points': points_3D,
        }

    # 使用边界线才用到这个
    global_lane_id = 0
    for road_id in pgd.progress(list(links_info.keys()), "数据解析中（2/8）"):
        # (1) 重新计算点，保证同一路段各条车道的断点的数量相同
        lanes_points = [lane["points"] for lane in links_info[road_id]["lanes_data"].values()]
        new_lanes_points = calculate_lanes_with_same_points(lanes_points, threshold_length, threshold_distance_max, threshold_distance_min, force=False)
        if not new_lanes_points:
            Logger.logger_network.warning(f"Link {road_id} does not meet the constraint conditions.")
            del links_info[road_id]
            continue

        for index, lane_id in enumerate(links_info[road_id]["lanes_data"].keys()):
            links_info[road_id]["lanes_data"][lane_id]["points"] = new_lanes_points[index]
        
        # (2) 分中心线和边界线，获取车道的左/中/右线
        # (2.1) 如果使用中心线
        if is_use_center_line:
            # 遍历该路段上的车道
            for lane_id, lane in links_info[road_id]["lanes_data"].items():
                lane_width = lane["width"]
                lane_points_centerLine = lane["points"]
                lane_points_threeLine = line2surface(lane_points_centerLine, {
                    "right": ['right', lane_width * 0.5],
                    "center": ['right', lane_width * 0],
                    "left": ['right', lane_width * -0.5],
                })
                links_info[road_id]["lanes_data"][lane_id]["points"] = lane_points_threeLine
        # (2.2) 如果使用边界线
        else:
            temp_data_roadId = []
            temp_data_type = []
            temp_data_points = []
            
            # 遍历该路段上的车道
            for lane_id, lane in links_info[road_id]["lanes_data"].items():
                road_id = lane["roadId"]
                temp_data_roadId.append(road_id)
                
                lane_type = lane["type"]
                temp_data_type.append(lane_type)
                
                lane_points_boundaryLine = lane["points"]
                temp_data_points.append(lane_points_boundaryLine)
            
            # 清空字典，不用原来的车道ID
            links_info[road_id]["lanes_data"].clear()
            
            # 获取边界线顺序，从右向左
            order = calculate_laneNumber_list(temp_data_points)

            for i in range(1, len(temp_data_points)):
                road_id = temp_data_roadId[order.index(i)]
                lane_type = temp_data_type[order.index(i)]

                # 取中值计算中心线点位
                rightLine = temp_data_points[order.index(i)]
                leftLine = temp_data_points[order.index(i+1)]
                centerLine = [tuple(v) for v in (np.array(rightLine) + np.array(leftLine)) / 2]
                
                lane_points_threeLine = {
                    "left": leftLine,
                    "right": rightLine,
                    "center": centerLine,
                    }
                
                links_info[road_id]["lanes_data"][global_lane_id] = {
                    'roadId': road_id,
                    'type': lane_type,
                    'points': lane_points_threeLine
                    }
                
                global_lane_id += 1
        
        # (3) 添加laneNumber
        lanes_points = [lane["points"]["center"] for lane in links_info[road_id]["lanes_data"].values()]
        # 获取车道序号列表
        laneNumber_list = calculate_laneNumber_list(lanes_points)
        # 添加laneNumber信息
        for index, lane_id in enumerate(links_info[road_id]["lanes_data"].keys()):
            links_info[road_id]["lanes_data"][lane_id]["laneNumber"] = laneNumber_list[index]
            
            # 保存单独车道信息
            lanes_info[lane_id] = links_info[road_id]["lanes_data"][lane_id]
            
        # 按车道序号排序，主要是为了中心线的情况
        links_info[road_id]["lanes_data"] = dict(sorted(links_info[road_id]["lanes_data"].items(), key=lambda item:item[1]["laneNumber"]))
    
    return links_info, lanes_info, other_info


# 获取连接段信息
def get_connector_info(folder_path, lanes_info, laneConnectorFileName="laneConnector"):
    # 文件路径
    filePath_dbf_laneConnector = os.path.join(folder_path, f"{laneConnectorFileName}.dbf")
    filePath_shp_laneConnector = os.path.join(folder_path, f"{laneConnectorFileName}.shp")

    # 如果没有连接段文件
    if not os.path.exists(filePath_dbf_laneConnector) or not os.path.exists(filePath_shp_laneConnector):
        return collections.defaultdict(list)
    
    # 读取数据
    try:
        all_data_dbf_laneConnector = list(dbfread.DBF(filePath_dbf_laneConnector, encoding='utf-8'))
        all_data_shp_laneConnector = shapefile.Reader(filePath_shp_laneConnector, encoding='utf-8').shapes()
    except:
        all_data_dbf_laneConnector = list(dbfread.DBF(filePath_dbf_laneConnector, encoding='gbk'))
        all_data_shp_laneConnector = shapefile.Reader(filePath_shp_laneConnector, encoding='gbk').shapes()
    
    # 保存连接段信息
    connector_info = collections.defaultdict(list)
    
    # 读取数据，并组合dbf数据和shp数据
    for index, laneConnector_data_shp in pgd.progress(enumerate(all_data_shp_laneConnector), "数据读取中（3/8）"):
        # 获取该路段的dbf数据
        laneConnector_data_dbf = all_data_dbf_laneConnector[index]
        
        # 经纬度转为平面坐标
        xy_list = [p(point[0], point[1]) for point in laneConnector_data_shp.points]
        
        # 判断属性z是否存在
        if hasattr(laneConnector_data_shp, "z"):
            z_list = laneConnector_data_shp.z
        else:
            z_list = [0 for i in range(len(xy_list))]
        
        # 获取上下游路段ID
        try:
            from_lane_id = laneConnector_data_dbf['preLaneId']
            to_lane_id = laneConnector_data_dbf['sucLaneId']
            from_lane_info = lanes_info[from_lane_id]
            to_lane_info = lanes_info[to_lane_id]
        except:
            Logger.logger_network.error(traceback.format_exc())
            continue
        
        # 车道连接的属性
        lane_type_from = from_lane_info["type"]
        lane_type_to = to_lane_info["type"]
        if lane_type_from != lane_type_to:
            continue

        lane_width = laneConnector_data_dbf.get('width') or default_lane_width.get(lane_type_from) or 3.5
        
        # 获取三维坐标
        points_3D = [[x, y, z] for (x, y), z in zip(xy_list, z_list)]
        
        lane_points_threeLine = line2surface(points_3D, {
            "right": ['right', lane_width * 0.5],
            "center": ['right', lane_width * 0],
            "left": ['right', lane_width * -0.5],
        })

        # 将同上下游路段的连接器放在一起
        connector_road_tuple = (from_lane_info['roadId'], to_lane_info['roadId'])
        connector_info[connector_road_tuple].append(
            {
                "from_lane_number": from_lane_info['laneNumber'],
                "to_lane_number": to_lane_info['laneNumber'],
                'points': lane_points_threeLine,
            }
        )

    return connector_info


# 根据距离新增连接属性
def get_new_connector_info(links_info, connector_info):
    nodes = []
    for road_id in pgd.progress(links_info, "数据解析中（4/8）"):
        for lane_info in links_info[road_id]["lanes_data"].values():
            lane_points = lane_info['points']["center"]
            nodes += [
                {
                    'point': lane_points[0],
                    'contactPoint': 'end',  # 车道起点、为连接的终点
                    'laneNumber': lane_info['laneNumber'],
                    'roadId': road_id,
                    'type': lane_info["type"]
                },
                {
                    'point': lane_points[-1],
                    'contactPoint': 'start',  # 车道终点、为连接的起点
                    'laneNumber': lane_info['laneNumber'],
                    'roadId': road_id,
                    'type': lane_info["type"]
                },
            ]

    # 寻找最近点
    node_points = [node['point'] for node in nodes]

    if node_points:
        # 用于快速查找的KDTree类
        kt = spt.KDTree(data=node_points, leafsize=10)

        # 获取距离较近的所有的点对
        node_groups = kt.query_pairs(join_point_distance)

        # 保持之前已经存在的连接段键值
        exist_connector_tuples = list(connector_info.keys())

        for node_group in pgd.progress(node_groups, "数据解析中（5/8）"):
            node_0, node_1 = nodes[node_group[0]], nodes[node_group[1]]
            # 如果link中的两个点既不在一条路段上，又不是同一起终类型，可以认为具有连接关系
            if node_0['roadId'] != node_1['roadId'] and node_0['contactPoint'] != node_1['contactPoint'] and node_0['type'] == node_1['type']:

                if node_0['contactPoint'] == 'start':
                    from_lane_info, to_lane_info = node_0, node_1
                else:
                    from_lane_info, to_lane_info = node_1, node_0
                connector_road_tuple = (from_lane_info['roadId'], to_lane_info['roadId'])
                from_lane_number, to_lane_number = from_lane_info['laneNumber'], to_lane_info['laneNumber']

                # 如果之前没有
                if connector_road_tuple not in exist_connector_tuples:
                    connector_info[connector_road_tuple].append(
                        {
                            "from_lane_number": from_lane_number,
                            "to_lane_number": to_lane_number,
                        }
                    )
    
    return connector_info


# 对拓宽段进行处理，窄的地方直接裁掉（导入边界线才用到）
def get_new_links_info(links_info):
    for road_id in pgd.progress(list(links_info.keys()), "数据解析中（6/8）"):
        # 只有该路段有至少两条车道才进行处理
        if len(links_info[road_id]["lanes_data"]) == 1:
            continue

        # 分别处理左侧拓宽和右侧拓宽的情况
        for num in [0, -1]:
            lane_id = list(links_info[road_id]["lanes_data"].keys())[num]
            lane_data = links_info[road_id]["lanes_data"][lane_id]
            leftLine = lane_data["points"]["left"]
            rightLine = lane_data["points"]["right"]
            # 只把大于最小宽度的点序号接入临时列表
            temp_list = []
            for j in range(len(leftLine)):
                left_x, left_y = leftLine[j][0], leftLine[j][1]
                right_x, right_y = rightLine[j][0], rightLine[j][1]
                distance = ((left_x - right_x) ** 2 + (left_y - right_y) ** 2) ** 0.5
                # 小于一定宽度路段要删除
                if distance >= min_width:
                    temp_list.append(j)
            # 如果有比较窄的地方
            if len(temp_list) != len(links_info[road_id]["lanes_data"][lane_id]["points"]["left"]):
                # N车道的路段
                for lane_id in links_info[road_id]["lanes_data"]:
                    for j in ["left", "center", "right"]:
                        links_info[road_id]["lanes_data"][lane_id]["points"][j] = [
                            links_info[road_id]["lanes_data"][lane_id]["points"][j][k] for k in temp_list]
    
    return links_info


def get_data(folder_path, is_use_lon_and_lat, is_use_center_line, laneFileName, laneConnectorFileName, proj_mode=None):
    # 读取路段数据
    links_info, lanes_info, other_info = get_links_info(folder_path, is_use_lon_and_lat, is_use_center_line, laneFileName, proj_mode)
    
    # 导入的中心线
    if is_use_center_line:
        # 读取连接段数据
        connector_info = get_connector_info(folder_path, lanes_info, laneConnectorFileName)
    # 导入的边界线
    else:
        connector_info = collections.defaultdict(list)
    
    # 对距离过近的自动连接
    connector_info = get_new_connector_info(links_info, connector_info)
    
    # 处理渐变段
    if not is_use_center_line:
        links_info = get_new_links_info(links_info)
    else:
        # 虚拟进度条
        for _ in pgd.progress(range(100), "数据解析中（6/8）"):
            pass
    
    return links_info, connector_info, other_info