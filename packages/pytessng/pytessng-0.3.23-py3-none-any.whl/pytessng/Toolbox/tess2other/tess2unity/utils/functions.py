from math import ceil, sqrt
from numpy import square
from PySide2.QtGui import QVector3D
from .config import sceneScale


def p2m(x):
    return x * sceneScale

def qtpoint2point(qtpoints):
    points = []
    for qtpoint in qtpoints:
        points.append(
            [p2m(qtpoint.x()), - p2m(qtpoint.y()), p2m(qtpoint.z())] if isinstance(qtpoint, QVector3D) else qtpoint
        )
    return points

def xyz2xzy(array):
    return [array[0], array[2], array[1]]

# 根据左右点序列创建三角形
def create_curve(left_points, right_points, split=False):
    # 三角形列表
    triangles = []
    for index, distance in enumerate(left_points[:-1]):  # 两两组合，最后一个不可作为首位

        # TODO 断线时，需要细分路段，做到步长均匀
        # 虚线受步长(断点列表)和虚实比例影响，需要额外处理
        # if split and index % 10 in [0, 1, 2, 3]:
        #     # 断线 3:2 虚线长度由步长和比例共同控制
        #     continue

        left_0, left_1, right_0, right_1 = left_points[index], left_points[index + 1], right_points[index], \
                                           right_points[index + 1]
        coo_0 = [left_0, left_1, right_0]
        coo_1 = [left_1, right_1, right_0]
        triangles.append(coo_0)
        triangles.append(coo_1)

    return triangles

def chunk(lst, size):
    return list(
        map(lambda x: lst[x * size:x * size + size],
            list(range(0, ceil(len(lst) / size)))))

def deviation_point(coo1, coo2, width, right=False, is_last=False):
    signl = 1 if right else -1  # 记录向左向右左右偏移
    x1, y1, z1, x2, y2, z2 = coo1 + coo2  # 如果是最后一个点，取第二个 点做偏移
    x_base, y_base, z_base = coo1 if not is_last else coo2
    if not ((x2 - x1) or (y2 - y1)):  # 分母为0
        return [x_base, y_base, z_base]
    X = x_base + signl * width * (y2 - y1) / sqrt(square(x2 - x1) + square((y2 - y1)))
    Y = y_base + signl * width * (x1 - x2) / sqrt(square(x2 - x1) + square((y2 - y1)))
    return [X, Y, z_base]

def calc_boundary(base_points, border_line_width):
    left_points, right_points = [], []
    point_count = len(base_points)
    for index, _ in enumerate(base_points):
        if index + 1 == point_count:
            is_last = True
            num = index - 1
        else:
            is_last = False
            num = index
        left_point = deviation_point(base_points[num], base_points[num + 1], border_line_width / 2, right=False,
                                     is_last=is_last)
        right_point = deviation_point(base_points[num], base_points[num + 1], border_line_width / 2, right=True,
                                      is_last=is_last)
        left_points.append(left_point)
        right_points.append(right_point)
    return left_points, right_points

