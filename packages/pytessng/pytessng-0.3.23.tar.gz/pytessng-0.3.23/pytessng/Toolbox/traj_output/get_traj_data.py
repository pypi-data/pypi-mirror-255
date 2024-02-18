import time
import math
from typing import Callable


def get_traj_data(simuiface, proj:Callable, p2m:Callable, move:dict):
    # 当前正在运行车辆列表
    lAllVehi = simuiface.allVehiStarted()
    # 当前已仿真时间，单位：毫秒
    simu_time = simuiface.simuTimeIntervalWithAcceMutiples()
    # 开始仿真的现实时间戳，单位：毫秒
    start_time = simuiface.startMSecsSinceEpoch()
    # 当前仿真计算批次
    batchNum = simuiface.batchNumber()

    traj_data = {
        "timestamp": str(int(time.time() * 1000)),
        "simuTime": simu_time,
        'startSimuTime': start_time,
        "batchNum": batchNum,
        "count": len(lAllVehi),
        "objs": [],
    }
    
    for vehi in lAllVehi:
        x = p2m(vehi.pos().x()) + move["x_move"]
        y = -p2m(vehi.pos().y()) + move["y_move"]
        if math.isnan(x) or math.isnan(y):
            continue

        lon, lat = proj(x, y, inverse=True)

        in_link = vehi.roadIsLink()
        lane = vehi.lane()

        # 车辆寻找异常，跳过
        if (in_link and not vehi.lane()) or (not in_link and not vehi.laneConnector()):
            continue

        angle = vehi.angle()
        veh_data = {
            "id": vehi.id(),
            'typeCode': vehi.vehicleTypeCode(),
            'roadId': vehi.roadId(),
            'inLink': in_link,
            'laneCount': in_link and lane.link().laneCount(),
            'laneNumber': in_link and lane.number(),
            'laneTypeName': in_link and lane.actionType(),
            'angle': angle,
            'speed': p2m(vehi.currSpeed()),
            'Speed': p2m(vehi.currSpeed()) * 3.6,
            'size': [p2m(vehi.length()), 2, 2],
            'color': "",
            'x': x,
            'y': y,
            'z': vehi.v3z(),
            'longitude': lon,
            'latitude': lat,
            'eulerX': -angle / 180 * math.pi + math.pi / 2,
            'eulerY': -angle / 180 * math.pi + math.pi / 2,
            'eulerZ': -angle / 180 * math.pi + math.pi / 2,
        }

        traj_data['objs'].append(veh_data)

    return traj_data

