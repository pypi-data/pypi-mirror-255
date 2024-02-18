import os
import shapefile
from .utils import config


def shape2tess(netiface, params):
    # params:
    # - folder_path
    # - is_use_center_line
    # - is_use_lon_and_lat
    # - laneFileName
    # - laneConnectorFileName
    # - proj_mode
    
    folder_path = params["folder_path"]
    is_use_lon_and_lat = params["is_use_lon_and_lat"]
    is_use_center_line = params["is_use_center_line"]
    laneFileName = params["laneFileName"]
    laneConnectorFileName = params["laneConnectorFileName"]
    proj_mode = params["proj_mode"]
    
    config.sceneScale = netiface.sceneScale()
    
    from .utils.get_data import get_data
    from .utils.create_network import create_network
    
    # 读取数据
    links_info, connector_info, other_info = get_data(folder_path, is_use_lon_and_lat, is_use_center_line, laneFileName, laneConnectorFileName, proj_mode)

    # import json
    # links_info_save = eval(str(dict(links_info)))
    # connector_info_save = {str(k):v for k,v in eval(str(dict(connector_info))).items()}
    # data = {"link": links_info_save, "connector": connector_info_save}
    # with open('data.json', 'w') as json_file:
    #     json.dump(data, json_file, indent=4)

    # 创建路段和连接段
    if links_info:
        create_network(netiface, links_info, connector_info, other_info)
        status, message = True, None
    else:
        status, message = False, "所选文件中无数据或无合法数据"

    return status, message



# 核查shape文件的坐标类型
def check_shapefile(folder_path, laneFileName, is_use_lon_and_lat):
    # 文件路径
    filePath_shp_lane = os.path.join(folder_path, f"{laneFileName}.shp")

    # 读取文件
    try:
        all_data_shp_lane = shapefile.Reader(filePath_shp_lane, encoding='utf-8').shapes()
    except:
        all_data_shp_lane = shapefile.Reader(filePath_shp_lane, encoding='gbk').shapes()

    # 坐标范围
    x_list, y_list = [], []
    for lane_data_shp in all_data_shp_lane:
        x_list.extend([point[0] for point in lane_data_shp.points])
        y_list.extend([point[1] for point in lane_data_shp.points])

    x_diff = max(x_list) - min(x_list)
    y_diff = max(y_list) - min(y_list)

    # 经纬度坐标
    if is_use_lon_and_lat:
        # 一定不是
        if min(x_list) < -180 or max(x_list) > 180 or min(y_list) < -90 or max(y_list) > 90:
            is_ok = False
            prompt_information = "判断为笛卡尔坐标，请检查！"
        # 大概率不是
        elif x_diff > 2 or y_diff > 2:
            is_ok = False
            prompt_information = "极大概率为笛卡尔坐标，请检查！"
        # 大概率是
        else:
            is_ok = True
            prompt_information = ""
    # 笛卡尔坐标
    else:
        # 很可能不是
        if x_diff < 1 and y_diff < 1:
            is_ok = False
            prompt_information = "极大概率为经纬度坐标，请检查！"
        else:
            is_ok = True
            prompt_information = ""

    return is_ok, prompt_information