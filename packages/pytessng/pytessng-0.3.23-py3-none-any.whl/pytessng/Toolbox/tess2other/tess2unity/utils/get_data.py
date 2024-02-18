import math
import collections
from .config import border_line_width, convert_attribute_mapping
from .functions import qtpoint2point, xyz2xzy, create_curve, chunk, calc_boundary


# 获取 路网三角形
def get_triangle_polygon(netiface):
    polygon_info = collections.defaultdict(list)

    # 绘制路面(黑色)
    for link in netiface.links():
        left_points = qtpoint2point(link.leftBreakPoint3Ds())
        right_points = qtpoint2point(link.rightBreakPoint3Ds())
        polygon_info["black"] += create_curve(left_points, right_points)
    for connector in netiface.connectors():
        for laneConnector in connector.laneConnectors():
            left_points = qtpoint2point(laneConnector.leftBreakPoint3Ds())
            # 防止 nan 情况发生(长度为0的情况)
            left_points = [_ for _ in left_points if not math.isnan(_[2])]
            right_points = qtpoint2point(laneConnector.rightBreakPoint3Ds())
            polygon_info["black"] += create_curve(left_points, right_points)

    # 绘制左右边界线(黄色实线，白色实线，白色虚线)
    for link in netiface.links():
        lanes = list(link.lanes())
        for index, lane in enumerate(lanes):
            if index == 0:
                # 最右侧车道绘制右侧边界(白色实线)
                base_points = qtpoint2point(link.rightBreakPoint3Ds())
                left_points, right_points = calc_boundary(base_points, border_line_width)
                polygon_info['white'] += create_curve(left_points, right_points)
            # 所有车道绘制左侧边界
            if lane == lanes[-1]:
                # 最左侧车道绘制黄色实线
                base_points = qtpoint2point(link.leftBreakPoint3Ds())
                left_points, right_points = calc_boundary(base_points, border_line_width)
                polygon_info['yellow'] += create_curve(left_points, right_points)
            elif lane.actionType() != lanes[index+1].actionType():
                # 左侧相邻车道类型不一致，绘制白色实线
                base_points = qtpoint2point(link.leftBreakPoint3Ds())
                left_points, right_points = calc_boundary(base_points, border_line_width)
                polygon_info['white'] += create_curve(left_points, right_points)
            else:
                # # 左侧相邻车道类型一致，绘制白色虚线
                base_points = qtpoint2point(link.leftBreakPoint3Ds())
                left_points, right_points = calc_boundary(base_points, border_line_width)
                polygon_info['white'] += create_curve(left_points, right_points, split=True)
    
    return polygon_info


def get_info(netiface):
    # 获取三角形数据
    polygon_data = get_triangle_polygon(netiface)

    # 存储最终的unity三角形信息
    unity_triangle_data = collections.defaultdict(list)

    for color, triangles in polygon_data.items():
        unity_attribute = convert_attribute_mapping[color]
        # 存储最终的 unity 数据
        for triangle in triangles:
            # 遍历每一个原始三角形点位
            for point in triangle:
                # unity 坐标系问题，需要 xyz 转 xzy, 同时将三维列表转换为一维列表
                new_point = xyz2xzy(point)
                # unity 是一个二维数组，元素为每个点的坐标，默认每三个点构成一个三角形
                unity_triangle_data[unity_attribute].append(new_point)

    # 转换为 unity数据
    unity_count = {}
    for key, value in unity_triangle_data.items():
        # unity 单次接收的三角形数量有限制，不能超过 256 * 256 个
        unity_triangle_data[key] = [
            {'pointsArray': info, 'drawOrder': [i for i in range(len(info))], 'count': int(len(info))}
            for info in chunk(value, 60000)]
        unity_count[key] = len(unity_triangle_data[key])

    # 三角形数量
    unity_data = {'unity': unity_triangle_data, 'count': {}}
    for k, v in unity_data['unity'].items():
        unity_data['count'][k] = len(v)

    return unity_data