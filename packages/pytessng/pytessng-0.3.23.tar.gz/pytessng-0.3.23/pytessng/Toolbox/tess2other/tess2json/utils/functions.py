import math
from .config import sceneScale


def p2m(x):
    return x * sceneScale

# 转换格式
def qtpoint2point(qt_points, mode="tess", projection=None, move=None):
    if move is None:
        x_move, y_move = 0, 0
    else:
        x_move, y_move = -move["x_move"], -move["y_move"]

    points = []
    for qt_point in qt_points:
        x = p2m(qt_point.x())
        y = -p2m(qt_point.y())
        z = p2m(qt_point.z())
        
        x += x_move
        y += y_move
        
        if mode == "real":
            x, y = projection(x, y, inverse=True)
        points.append([x, y, z])

    return points

# 求两点连线与y正轴的夹角
def calculate_angle_with_y_axis(location1, location2):
    x1, y1, _ = location1
    x2, y2, _ = location2
    delta_x = x2 - x1
    delta_y = y2 - y1
    # 使用 atan2 计算角度（弧度）
    angle_rad = math.atan2(delta_x, delta_y)
    # 将弧度转换为角度
    angle_deg = math.degrees(angle_rad)
    # 将角度限制在0到360
    angle_deg_with_y_axis = (angle_deg + 360) % 360

    return angle_deg_with_y_axis
