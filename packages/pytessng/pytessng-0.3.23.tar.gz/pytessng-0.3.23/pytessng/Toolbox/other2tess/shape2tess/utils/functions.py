import math
import random
import string
import numpy as np
from PySide2.QtGui import QVector3D
from .config import sceneScale
from .....Tessng.MyMenu import Logger


def m2p(x):
    return x / sceneScale

def get_coo_list(vertices):
    list1 = []
    x_move, y_move = 0, 0
    for index in range(0, len(vertices), 1):
        vertice = vertices[index]
        list1.append(QVector3D(m2p((vertice[0] - x_move)), m2p(-(vertice[1] - y_move)), m2p(vertice[2])))
    if len(list1) < 2:
        raise 3
    return list1

###############################################################################

# 计算给定经度下两个纬度点的中心位置的纬度和经度
def calculate_center(lat_min, lat_max, lon_min, lon_max):
    # 计算中心位置的经度
    lon_center = (lon_min + lon_max) / 2

    # 将纬度和经度从度数转换为弧度
    lat1 = math.radians(lat_min)
    lat2 = math.radians(lat_max)
    # 计算中心位置的纬度
    lat_center = (lat1 + lat2) / 2
    # 将中心位置的纬度和经度从弧度转换为度数
    lat_center = math.degrees(lat_center)

    return lon_center, lat_center


# 生成随机字符串
def generate_random_string(length=9):
    # 可用字符集合，包括字母和数字
    characters = string.ascii_letters + string.digits

    # 生成随机字符串
    random_string = ''.join(random.choice(characters) for _ in range(length))

    return random_string

###############################################################################
# 计算具有相同点数的车道断点列表
# calculate_lanes_with_same_points
# - all_lanes
# - threshold_length=3
# - threshold_distance_max=5
# - threshold_distance_min=1
# - force=False

# 计算两点之间的直线距离
def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

# 对车道起终点之间的距离合理性进行判断
def check_lane_points(all_lanes, threshold_distance_max, threshold_distance_min):
    # 如果该路段只有一条车道
    if len(all_lanes) == 1:
        return True
    
    # 对每条车道的起点（终点）进行判断，在其他车道中，是否至少有一条车道的起点（终点）与本车道的起点（终点）在一定范围内
    for idx, lane in enumerate(all_lanes):
        start_point = lane[0]
        end_point = lane[-1]
        
        found_connection_start = False
        found_connection_end = False
        
        for other_idx, other_lane in enumerate(all_lanes):
            # 不和自己比较
            if idx != other_idx:
                other_start = other_lane[0]
                other_end = other_lane[-1]
                
                # 判断起点和其他车道的起点是否满足条件
                distance = calculate_distance(start_point, other_start)
                if distance <= threshold_distance_max:
                    found_connection_start = True
                
                # 判断终点和其他车道的终点是否满足条件
                distance = calculate_distance(end_point, other_end)
                if distance <= threshold_distance_max:
                    found_connection_end = True
                
                if found_connection_start and found_connection_end:
                    break
        
        if not found_connection_start or not found_connection_end:
            Logger.logger_network.warning("Shape: The distance between the starting or ending points of two lanes in a link is too far!")
            return False
    
    # 车道起终点之间的距离不能过小
    for idx, lane in enumerate(all_lanes):
        start_point = lane[0]
        end_point = lane[-1]
        
        for other_idx, other_lane in enumerate(all_lanes):
            # 不和自己比较
            if idx != other_idx:
                other_start = other_lane[0]
                other_end = other_lane[-1]
                
                # 判断起点和其他车道的起点是否满足条件
                distance = calculate_distance(start_point, other_start)
                if distance < threshold_distance_min:
                    Logger.logger_network.warning(f"Shape: The distance {distance:.1f}m between the starting points of two lanes in a link is too close!")
                    return False
                
                # 判断终点和其他车道的终点是否满足条件
                distance = calculate_distance(end_point, other_end)
                if distance < threshold_distance_min:
                    Logger.logger_network.warning(f"Shape: The distance {distance:.1f}m between the ending points of two lanes in a link is too close!")
                    return False
    
    return True

# 计算车道长度
def calculate_lane_length(one_lane):
    total_length = 0
    for i in range(1, len(one_lane)):
        total_length += calculate_distance(one_lane[i], one_lane[i-1])
    return total_length

# 检查最长的车道与最短的车道的长度差是否在一定范围内
def check_lane_length(all_lanes, threshold_length):
    lane_lengths = [calculate_lane_length(lane) for lane in all_lanes]
    min_lane_length = min(lane_lengths)
    max_lane_length = max(lane_lengths)
    
    if max_lane_length - min_lane_length <= threshold_length:
        return np.mean(lane_lengths)
    else:
        Logger.logger_network.warning(f"Shape: The longest lane is -max: {max_lane_length:.1f}m, and the shortest lane is {min_lane_length:.1f}m.")
        return False

# 计算每个断点到起点的距离占整个车道长度的比例（%）
def calculate_distance_proportions(one_lane):
    cumulative_distances_to_start = [0]
    for i in range(1, len(one_lane)):
        distance = calculate_distance(one_lane[i], one_lane[i - 1])
        cumulative_distances_to_start.append(cumulative_distances_to_start[-1] + distance)
    # 车道总长度
    total_lane_length = cumulative_distances_to_start[-1]
    
    proportions = [distance / total_lane_length for distance in cumulative_distances_to_start]

    return proportions

# 计算多条车道的每个断点到起点的距离比例，并合并并去重
def calculate_merged_proportions(all_lanes, mean_length):
    merged_proportions = []
    
    for lane in all_lanes:
        proportions = calculate_distance_proportions(lane)
        merged_proportions.extend(proportions)
    
    # # 使N米一个点
    # new_list = [i/mean_length for i in range(1, int(mean_length), 3)]
    # merged_proportions.extend(new_list)
    
    # 保留两位小数，去重，排序
    merged_proportions = sorted(list(set([round(num, 2) for num in merged_proportions])))
    
    return merged_proportions

# 线性插值函数
def linear_interpolation(point1, point2, alpha):
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    x = x1 + alpha * (x2 - x1)
    y = y1 + alpha * (y2 - y1)
    z = z1 + alpha * (z2 - z1)
    return x, y, z

# 计算每条车道上相对应比例位置的坐标点
def calculate_interpolated_points(all_lanes, merged_proportions):
    interpolated_lanes_data = []
    for lane in all_lanes:
        interpolated_points = []
        # 每条车道上每个断点到起点的距离比例
        proportions = calculate_distance_proportions(lane)
        for proportion in merged_proportions:
            i = 0
            while i < len(proportions) - 1 and proportions[i + 1] < proportion:
                i += 1
            if proportions[i + 1] == proportions[i]:
                alpha = 0
            else:
                alpha = (proportion - proportions[i]) / (proportions[i + 1] - proportions[i])
            interpolated_point = linear_interpolation(lane[i], lane[i + 1], alpha)
            interpolated_points.append(interpolated_point)
        
        interpolated_lanes_data.append(interpolated_points)
    
    return interpolated_lanes_data


# 输入多条车道数据，返回有共同断点数量的车道数据
def calculate_lanes_with_same_points(all_lanes, threshold_length=3, threshold_distance_max=5, threshold_distance_min=1, force=False):
    # 若强制计算，则跳过检查步骤
    if force:
        Logger.logger_network.warning("Shape: Forced calculation!")
    else:
        # 检查最长的车道与最短的车道的长度差是否在一定范围内
        mean_length = check_lane_length(all_lanes, threshold_length)
        if not mean_length:
            Logger.logger_network.warning("Shape: The difference in length between the longest and shortest lanes exceeds the threshold!")
            return None
        
        # 在其他车道中，是否至少有一条车道的起/终点与本车道的起/终点在一定范围内
        if not check_lane_points(all_lanes, threshold_distance_max, threshold_distance_min):
            Logger.logger_network.warning("Shape: The distance between the starting and ending points of a certain lane and those of other lanes is not within a reasonable range!")
            return None
    
    # 计算合并后的距离比例列表
    merged_proportions = calculate_merged_proportions(all_lanes, mean_length)
    
    # 计算插值后的坐标点
    interpolated_points = calculate_interpolated_points(all_lanes, merged_proportions)
    
    return interpolated_points

###############################################################################
# 计算车道序号
# calculate_laneNumber_list
# - lanes_points
# - threshold_distance=2

def calculate_laneNumber_list(lanes_points, threshold_distance=2):
    # 找到一条车道作为基准车道
    base_lane = lanes_points[0]

    # 如果大于等于三个点，就用第二个点和第三个点；否则就用第一个点和第二个点
    if len(base_lane) >= 3:
        num_last, num_next = 1, 2
    else:
        num_last, num_next = 0, 1

    # 计算基准车道的方向向量，使用前两个点
    base_direction = np.array(base_lane[num_next]) - np.array(base_lane[num_last])

    # 计算基准车道的旋转角度（逆时针方向）
    angle_to_rotate = np.arctan2(base_direction[0], base_direction[1])

    # 使用旋转矩阵将所有车道旋转到指向y正轴
    rotation_matrix = np.array([[np.cos(angle_to_rotate), -np.sin(angle_to_rotate)],
                                [np.sin(angle_to_rotate), np.cos(angle_to_rotate)]])

    # 获取旋转后的各车道第一个点的x坐标
    x_coordinates = [np.dot(rotation_matrix, np.array(lane[num_last][:2]))[0] for lane in lanes_points]
    
    # 获取车道索引，从右向左，从1开始
    sorted_indices = len(x_coordinates) - np.argsort(np.argsort(x_coordinates))
    
    return list(sorted_indices)

###############################################################################
# 根据车道中心点向左右偏移
# line2surface
# - base_points
# - move_parameters

def deviation_point(coo1, coo2, width, right=False, is_last=False):
    signl = 1 if right else -1  # 记录向左向右左右偏移
    x1, y1, z1, x2, y2, z2 = list(coo1) + list(coo2)  # 如果是最后一个点，取第二个 点做偏移
    x_base, y_base, z_base = (x1, y1, z1) if not is_last else (x2, y2, z2)
    if not ((x2 - x1) or (y2 - y1)):  # 分母为0
        return [x_base, y_base, z_base]
    X = x_base + signl * width * (y2 - y1) / np.sqrt(np.square(x2 - x1) + np.square((y2 - y1)))
    Y = y_base + signl * width * (x1 - x2) / np.sqrt(np.square(x2 - x1) + np.square((y2 - y1)))
    return [X, Y, z_base]


def line2surface(base_points, move_parameters: dict):
    """
    Args:
        base_points:
        move_parameters:     {
        "right": ['right', 4],
        "center": ['right', 2],
        "left": ['right', 0],
    }
    根据基础点序列，及偏移方向和偏移量进行偏移(['right', 4])
    Returns:

    """
    points = {
        "right": [],
        "center": [],
        "left": [],
    }
    point_count = len(base_points)
    for index in range(point_count):
        if index + 1 == point_count:
            is_last = True
            num = index - 1
        else:
            is_last = False
            num = index

        for position, parameter in move_parameters.items(): #左/中/右
            direction, width = parameter
            point = deviation_point(base_points[num], base_points[num + 1], width, right=(direction == 'right'), is_last=is_last)
            points[position].append([point[0], point[1], base_points[index][2]])
    return points

