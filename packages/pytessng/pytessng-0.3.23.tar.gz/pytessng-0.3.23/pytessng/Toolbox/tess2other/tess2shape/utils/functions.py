from PySide2.QtGui import QVector3D
from .config import sceneScale


def p2m(x):
    return x * sceneScale

def qtpoint2point(qtpoints, move=None):
    if move is None:
        x_move, y_move = 0, 0
    else:
        x_move, y_move = -move["x_move"], -move["y_move"]

    points = []
    for qt_point in qtpoints:
        x = p2m(qt_point.x())
        y = -p2m(qt_point.y())
        z = p2m(qt_point.z())
        x += x_move
        y += y_move
        points.append([x, y, z])
    return points

# 坐标转经纬度
def point2latlon(points, p):
    new_points = []
    for point in points:
        lon, lat = p(point[0], point[1], inverse=True)
        new_points.append([lon, lat, point[2]])
    # 返回经纬度坐标及z坐标列表
    return new_points


