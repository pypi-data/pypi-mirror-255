from PySide2.QtGui import QVector3D
from PySide2.QtCore import QPointF
from .config import sceneScale


def m2p(x):
    return x / sceneScale

def get_coo_list(vertices):
    list1 = []
    x_move, y_move = 0, 0
    for index in range(0, len(vertices), 1):
        vertice = vertices[index]
        if len(vertice) == 3:
            list1.append(QVector3D(m2p((vertice[0] + x_move)), m2p(-(vertice[1]) + y_move), m2p(vertice[2])))
        elif len(vertice) == 2:
            list1.append(QPointF(m2p((vertice[0] + x_move)), m2p(-(vertice[1]) + y_move)))
    if len(list1) < 2:
        raise 3
    return list1
