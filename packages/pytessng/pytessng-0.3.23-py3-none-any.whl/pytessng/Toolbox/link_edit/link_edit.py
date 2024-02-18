from PySide2.QtGui import QVector3D
from PySide2.QtCore import QPointF
from .utils.functions import AdjustNetwork, simplify_tessng_file

###############################################################################

# 更新路网比例尺
def update_sceneScale(netiface):
    from .utils import config
    # 场景比例尺
    config.sceneScale = netiface.sceneScale()


# 创建路段
def createLink(netiface, laneCount, laneWidth, lanePoints):
    # 更新场景比例尺
    update_sceneScale(netiface)
    from .utils.functions import m2p

    points = [point.split(",") for point in lanePoints.split(";")]
    if len(points[0]) == 2:
        points = [QPointF(m2p(float(point[0])), - m2p(float(point[1]))) for point in points]
        netiface.createLinkWithLaneWidth(points, [laneWidth for _ in range(laneCount)])
    else:
        points = [QVector3D(m2p(float(point[0])), - m2p(float(point[1])), m2p(float(point[2]))) for point in points]
        netiface.createLink3DWithLaneWidth(points, [laneWidth for _ in range(laneCount)])


# 打断路段
def splitLink(netiface, link_id:int, pos:tuple):
    # 更新场景比例尺
    update_sceneScale(netiface)
    from .utils.functions import m2p

    distToStart = None
    split_pos_x, split_pos_y = m2p(pos[0]), -m2p(pos[1])
    locations = netiface.locateOnCrid(QPointF(split_pos_x, split_pos_y), 9)
    for location in locations:
        # 因为 C++ 和 Python 调用问题，必须先把 lane 实例化再赋值
        if not location.pLaneObject.isLane():
            return

        lane = location.pLaneObject.castToLane()
        if not (lane.link().id() == link_id):
            return

        distToStart = location.distToStart
        leastDist = location.leastDist
        location_x, location_y = location.point.x(), location.point.y()
        print("寻找到最近点", link_id, (split_pos_x, split_pos_y), (location_x, location_y), leastDist)
        break

    if distToStart is None:
        return
    split_distances = [[link_id, distToStart]]
    adjust_obj = AdjustNetwork(netiface)
    message = adjust_obj.split_link(split_distances)
    print(message)


# 连接路段
def joinLink(netiface):
    # 更新场景比例尺
    update_sceneScale(netiface)

    # 如果没有路段
    if not netiface.linkCount():
        message = "当前没有路段！"
        return False, message
    
    adjust_obj = AdjustNetwork(netiface)
    message = adjust_obj.join_link()
    
    return True, message


# 简化路网
def simplifyTessngFile(netiface, file_path, angle=1, length=50):
    try:
        message = simplify_tessng_file(file_path, angle, length)
        netiface.openNetFle(file_path)
        return True, message
    except:
        message = "路网简化失败, 请联系开发者"
        return False, message
