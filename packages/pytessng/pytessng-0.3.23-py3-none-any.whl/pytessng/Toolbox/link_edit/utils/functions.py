import json
import sqlite3
from typing import Dict, List
import collections
import numpy as np
from PySide2.QtGui import QVector3D
from .config import *
from .functions2 import get_new_point_indexs

###############################################################################

def p2m(x):
    return x * sceneScale

def m2p(x):
    return x / sceneScale

###############################################################################

def qtpoint2point(qtpoints):
    points = []
    for qtpoint in qtpoints:
        points.append(
            [m2p(qtpoint.x()), - m2p(qtpoint.y()), m2p(qtpoint.z())] if isinstance(qtpoint, QVector3D) else qtpoint
        )
    return points


def point2qtpoint(points):
    qtpoints = []
    for point in points:
        qtpoints.append(
            QVector3D(p2m(point[0]), - p2m(point[1]), p2m(point[2])) if not isinstance(point, QVector3D) else point
        )
    return qtpoints


###############################################################################

class Road:
    def __init__(self):
        self.link = None
        self.last_links = []
        self.next_links = []
        self.connectors = []  # 暂时没用到


class AdjustNetwork:
    def __init__(self, netiface):
        self.netiface = netiface
        self.roads = self.calc_connector()

        self.connector_area_mapping = self.calc_connector_area()

        # 在调整的过程中，旧的link在不断删除，同时新的link被创建，所以需要建立映射关系表
        # connector也有可能在消失，所以不再被记录，通过上下游link获取connector
        self.old_new_link_mapping = {}
        # 初始化映射表,link在调整前后可能存在一对多/多对一关系，所以用 dict&list 记录
        for link in netiface.links():
            self.old_new_link_mapping[link.id()] = [link.id()]

    # 记录全域的连接段面域
    def calc_connector_area(self):
        connector_area_mapping = collections.defaultdict(list)
        for ConnectorArea in self.netiface.allConnectorArea():
            for connector in ConnectorArea.allConnector():
                connector_area_mapping[ConnectorArea.id()].append(connector.id())
        return connector_area_mapping


    # 记录全局的连接关系
    def calc_connector(self):
        roads = {}
        for connector in self.netiface.connectors():
            # 上下游不可能为空
            last_link = connector.fromLink()
            next_link = connector.toLink()

            last_road = roads.get(last_link.id(), Road())
            next_road = roads.get(next_link.id(), Road())

            last_road.link = last_link
            last_road.next_links.append(next_link.id())
            last_road.connectors.append(connector)

            next_road.link = next_link
            next_road.last_links.append(last_link.id())
            next_road.connectors.append(connector)

            roads[next_link.id()] = next_road
            roads[last_link.id()] = last_road

        # 记录无连接段的路段
        for link in self.netiface.links():
            if link.id() not in roads:
                road = Road()
                road.link = link
                roads[link.id()] = road
        return roads

    # 计算路段上所有的路段点，车道点
    # 根据已知的信息计算新的断点序列列表
    @staticmethod
    def calc_points(points, indexs_list, ratios):
        last_index = 0
        points = qtpoint2point(points)

        new_points_list = []  # [[] for _ in indexs_list]

        first_point = None
        # 先把初识点全部分配下去
        for _, indexs in enumerate(indexs_list):
            if indexs:
                last_index = indexs[-1]  # 更新计算点
            new_points = [points[index] for index in indexs]
            # 添加首尾点
            if first_point is not None:
                new_points.insert(0, first_point)

            ratio = ratios[_]
            final_point = np.array(points[last_index]) * (1 - ratio) + np.array(points[last_index + 1]) * ratio
            new_points.append(final_point)
            first_point = final_point

            new_points_list.append(new_points)
            # if indexs:
            #     last_index = indexs[-1]  # 更新计算点

        # 添加最后一个路段，第一个点为上一路段计算的终点，第二个点为上一路段所在点序列的下一个点，最后一个点为路段终点
        new_points_list.append([first_point] + points[last_index + 1:])
        new_points_list = [point2qtpoint(i) for i in new_points_list]
        return new_points_list

    def calc_split_parameter(self, link, split_link_info):
        center_points = link.centerBreakPoint3Ds()
        center_points = qtpoint2point(center_points)

        sum_length = 0
        last_x, last_y, last_z = center_points[0]
        lengths = [0] + split_link_info["lengths"]
        for point_index, point in enumerate(center_points):
            x, y, z = point
            distance = np.sqrt((x - last_x) ** 2 + (y - last_y) ** 2)
            last_x, last_y, last_z = x, y, z

            new_sum_length = sum_length + distance
            for split_index, split_length in enumerate(lengths):
                if split_index == 0:
                    continue
                if new_sum_length < lengths[split_index - 1]:
                    continue
                elif new_sum_length >= lengths[split_index - 1] and new_sum_length < lengths[split_index]:
                    # 区间命中
                    split_link_info['index'][split_index - 1].append(point_index)
                    # TODO 区间已经命中，可以 break 了
                # elif sum_length >= lengths[split_index - 1] and new_sum_length > split_length:
                #     # 新点超出范围,计算比例
                #     ratio = (split_length - sum_length) / distance
                #     split_link_info['ratio'][split_index - 1] = ratio  # 此处不需要记录 首点的比例，因为当需要用到首点时，采用上一点的断点计算
                else:  # new_sum_length >= lengths[split_index]
                    # 如果此处并没有 ratio，说明这是第一次被匹配上，需要进行ratio 计算
                    if split_link_info['ratio'][split_index - 1] is None:
                        ratio = (split_length - sum_length) / distance
                        split_link_info['ratio'][split_index - 1] = ratio  # 此处不需要记录 首点的比例，因为当需要用到首点时，采用上一点的断点计算
            sum_length = new_sum_length

        # 计算完成，可以进行分割
        if len(split_link_info['lengths']) != len(split_link_info['index']) or len(split_link_info['lengths']) != len(
                split_link_info['index']):
            raise 1  # 初步判断

    def calc_split_links_info(self, link, split_link_info):
        # 计算新的 link 信息
        indexs_list = split_link_info['index']
        ratios = split_link_info['ratio']
        link_center_points = self.calc_points(link.centerBreakPoint3Ds(), indexs_list, ratios)

        new_links_info = [
            {
                'center': link_center_points[index],
                # 'name': f"{link.name()}/{index}",
                'name': f"{link.name()}",  # 保留原路段名
                'lanes': collections.defaultdict(lambda: {
                    'center': [],
                    'left': [],
                    'right': [],
                    'type': '',
                    'attr': {},
                }),
                'old_link_id': link.id(),
            } for index in range(len(indexs_list) + 1)
        ]

        for lane in link.lanes():
            center_points = self.calc_points(lane.centerBreakPoint3Ds(), indexs_list, ratios)
            left_points = self.calc_points(lane.leftBreakPoint3Ds(), indexs_list, ratios)
            right_points = self.calc_points(lane.rightBreakPoint3Ds(), indexs_list, ratios)
            for index in range(len(indexs_list) + 1):  # 被分割后的 link 数量,比分割点数大 1
                new_links_info[index]['lanes'][lane.number()] = {
                    'center': center_points[index],
                    'left': left_points[index],
                    'right': right_points[index],
                    'type': lane.actionType(),
                    'attr': {},
                }
        return new_links_info

    def split_link(self, reader):
        split_links_info = collections.defaultdict(lambda: {'lengths': [], 'index': [], 'ratio': []})
        for row in reader:
            try:
                row = [float(i) for index, i in enumerate(row)]
            except:
                return f"输入数据错误:{row}"

            link_id = int(row[0])
            points_length = sorted(row[1:])
            link = self.netiface.findLink(link_id)
            if not link:
                return f"link: {link_id} 不存在"
            if min(points_length) <= 0 or max(points_length) >= link.length() or len(points_length) != len(
                    set(points_length)):
                return f"link: {row[0]} 长 {link.length()}, 断点长度输入不准确"

            split_links_info[link_id]['lengths'] = points_length
            split_links_info[link_id]['index'] = [[] for _ in points_length]
            split_links_info[link_id]['ratio'] = [None for _ in points_length]

        # 路段有可能发生 合并，切分，所以使用 list 存储最为合理
        old_new_link_mapping = collections.defaultdict(list)
        for link in self.netiface.links():
            old_new_link_mapping[link.id()].append(link.id())

        old_connectors = []
        # 记录原始连接信息
        for link_id in split_links_info.keys():
            # last_link, next_link 都不属于 link_group,所以在过程中可能已经被删除，只能通过id映射获取新的link
            # 可能存在多个上游路段和多个下游路段，需要逐个获取连接段，从而记录连接关系
            old_connectors += self.calc_upstream_connection(link_id)
            old_connectors += self.calc_downstream_connection(link_id)

        all_new_link_info = []
        # 计算新的路段信息
        for link_id, split_link_info in split_links_info.items():
            link = self.netiface.findLink(link_id)
            # 根据 link 实际信息 丰富 切割参数 > split_link_info
            self.calc_split_parameter(link, split_link_info)
            # 获取切割详情，含点序列等基本信息
            new_links_info = self.calc_split_links_info(link, split_link_info)
            all_new_link_info += new_links_info
            # 记录 link 基本信息后移除
            old_link_id = link.id()
            old_new_link_mapping[old_link_id].remove(old_link_id)  # 删除路段前，移除相关的映射关系
            self.netiface.removeLink(link)

        temp_link_mapping = collections.defaultdict(list)
        # 根据记录的信息, 集中创建新的路段并更新映射表
        for new_link_info in all_new_link_info:
            # 做路段分割时，原始路段有且仅有一个
            old_link_id = new_link_info['old_link_id']
            new_link_obj = self.create_new_link(new_link_info)
            # 记录进映射表
            old_new_link_mapping[old_link_id].append(new_link_obj.id())
            temp_link_mapping[old_link_id].append(new_link_obj.id())

        message = "路段分割结果: \n"
        for k, v in temp_link_mapping.items():
            message += f"{k} --> {v} \n"

        # 集中创建内部的连接段
        for old_link_id, new_link_ids in old_new_link_mapping.items():
            for index in range(len(new_link_ids) - 1):
                from_link_id = old_new_link_mapping[old_link_id][index]
                to_link_id = old_new_link_mapping[old_link_id][index + 1]
                link_obj = self.netiface.findLink(from_link_id)
                # 被分割的小路段的车道数/车道类型均完全一致，所以随便取一个路段即可
                lanes = [lane.number() + 1 for lane in link_obj.lanes()]
                self.netiface.createConnector(from_link_id, to_link_id, lanes, lanes, f"{from_link_id}-{to_link_id}")

        # 根据记录的信息 批量创建新的连接段
        self.create_all_new_connector(old_connectors, old_new_link_mapping)
        return message

    def join_link(self):
        # TODO 合并路段, 需要添加车道类型判断，后续增加点位自合并的方法
        link_groups = []
        exist_links = []
        for link_id, road in self.roads.items():
            if link_id in exist_links:
                # 已经进行过查找的 link 不需要再次遍历
                continue

            # 获取 link 相应的 上下游link 并组成有序列表
            link_group = [road.link]
            self.get_chain_by_next(road, link_group)
            self.get_chain_by_last(road, link_group)

            link_groups.append(link_group)
            exist_links += [i.id() for i in link_group]

        # 判断是否有路段进行过重复查询，如果有，说明逻辑存在漏洞
        if len(exist_links) != len(set(exist_links)):
            return "出现唯一性错误，请联系开发者"

        # 在调整的过程中，旧的link在不断删除，同时新的link被创建，所以需要建立映射关系表，connector也有可能在消失，所以不再被记录，通过上下游link获取connector
        # 初始化映射表, 为了和 分割路段保持一致，仍然采用 dict(list) 的形式，但实际上, 最后的 list 有且仅有一个值
        old_new_link_mapping = collections.defaultdict(list)
        for link in self.netiface.links():
            old_new_link_mapping[link.id()].append(link.id())

        # TODO 根据信息做路网调整, 在调整过程中，未遍历到的 link_group 不会被调整，即不会丢失对象
        # 分步做，先统计原始的连接段信息，方便后续迭代
        old_connectors = []
        for link_group in filter(lambda x: len(x) > 1, link_groups):
            # 记录原始信息，方便后续重新创建路段及连接段
            first_link = link_group[0]
            final_link = link_group[-1]

            # last_link, next_link 都不属于 link_group,所以在过程中可能已经被删除，只能通过id映射获取新的link
            # 可能存在多个上游路段和多个下游路段，需要逐个获取连接段，从而记录连接关系
            old_connectors += self.calc_upstream_connection(first_link.id())
            old_connectors += self.calc_downstream_connection(final_link.id())

        all_new_link_info = []
        all_remove_links = []
        # 记录路段合并信息
        for link_group in filter(lambda x: len(x) > 1, link_groups):
            new_link_info = {
                'center': [],
                'name': '',
                'lanes': collections.defaultdict(lambda: {
                    'center': [],
                    'left': [],
                    'right': [],
                    'type': '',
                    'attr': {},
                }),
                'old_link_ids': [i.id() for i in link_group],
            }

            # 先记录id
            for link in link_group:  # 有序的进行点位合并
                # TODO 暂时不记录中间连接段的点序列
                new_link_info['center'] += link.centerBreakPoint3Ds()
                new_link_info['name'] += link.name()
                for lane in link.lanes():
                    lane_number = lane.number()
                    new_link_info['lanes'][lane_number]['center'] += lane.centerBreakPoint3Ds()
                    new_link_info['lanes'][lane_number]['left'] += lane.leftBreakPoint3Ds()
                    new_link_info['lanes'][lane_number]['right'] += lane.rightBreakPoint3Ds()
                    new_link_info['lanes'][lane_number]['type'] = lane.actionType()

                # 记录 link 基本信息后移除
                # old_new_link_mapping[link.id()].remove(link.id())
                # self.netiface.removeLink(link)
            all_new_link_info.append(new_link_info)

        message = "路段合并结果: \n"
        # 集中创建新的路段并更新映射表
        for new_link_info in all_new_link_info:
            new_link_obj = self.create_new_link(new_link_info)

            # 新路段创建成功，进行老路段移除，并更新新的连接数据，否则不做处理
            if not new_link_obj:  # 新路段可能创建失败
                continue

            for old_link_id in new_link_info['old_link_ids']:
                old_link = self.netiface.findLink(old_link_id)
                old_new_link_mapping[old_link_id].remove(old_link_id)  # 旧路段的关联路段也移除
                self.netiface.removeLink(old_link)
            message += f"{new_link_info['old_link_ids']} --> {new_link_obj.id()} \n"
            # 更新映射表，原本多个旧路段都指向了同一个新路段
            for old_link_id in new_link_info['old_link_ids']:
                old_new_link_mapping[old_link_id].append(new_link_obj.id())

        # 创建新的连接段,
        # 如果某连接段上下游均进行了路段合并，则连接段会被重新重复创建，已被过滤
        self.create_all_new_connector(old_connectors, old_new_link_mapping)

        return message

    # 计算路段的上游连接关系
    def calc_upstream_connection(self, link_id):
        road = self.roads[link_id]
        connectors = []
        for last_link_id in road.last_links:
            connector_info = self.get_connector_info(last_link_id, link_id)
            connectors.append(connector_info)
        return connectors

    # 计算路段的下游连接关系
    def calc_downstream_connection(self, link_id):
        road = self.roads[link_id]
        connectors = []
        for next_link_id in road.next_links:
            connector_info = self.get_connector_info(link_id, next_link_id)
            connectors.append(connector_info)
        return connectors

    def get_connector_info(self, from_link_id, to_link_id):
        connector = self.netiface.findConnectorByLinkIds(from_link_id, to_link_id)
        return {
            'from_link_id': from_link_id,
            'to_link_id': to_link_id,
            'connector': [
                (i.fromLane().number(), i.toLane().number())
                for i in connector.laneConnectors()
            ],
            'lanesWithPoints3': [
                {
                    "center": i.centerBreakPoint3Ds(),
                    "left": i.leftBreakPoint3Ds(),
                    "right": i.rightBreakPoint3Ds(),
                }
                for i in connector.laneConnectors()
            ],
        }

    def get_chain_by_next(self, road, link_group: list):
        if len(road.next_links) != 1:
            # 有且仅有一个下游，才可以继续延伸
            return

        next_link_id = road.next_links[0]
        # 新增判断，即使路段只有一个下游，连接段所属面域中存在多个连接段，仍然不允许合并
        connector = self.netiface.findConnectorByLinkIds(road.link.id(), next_link_id)
        for value in self.connector_area_mapping.values():
            if connector.id() in value and len(value) >= 3:
                print(f"面域内连接段过多, 进入交叉口区域, 不再继续: {value}")
                return

        next_link = self.netiface.findLink(next_link_id)
        next_road = self.roads[next_link.id()]
        # 判断下游 link 是否有且仅有 1 个上游，且车道数/车道类型与当前link一致，若一致，加入链路并继续向下游寻找
        if len(next_road.last_links) == 1 and [lane.actionType() for lane in road.link.lanes()] == [
            lane.actionType() for lane in next_road.link.lanes()]:
            if next_link in link_group:
                # link已存在，说明构成了回路，直接结束
                return
            link_group.append(next_link)
            self.get_chain_by_next(next_road, link_group)
        return

    # 通过指定路段信息寻找匹配的上下游
    def get_chain_by_last(self, road, link_group: list):
        if len(road.last_links) != 1:
            # 有且仅有一个上游，才可以继续延伸
            return
        last_link_id = road.last_links[0]
        # 新增判断，即使路段只有一个下游，连接段所属面域中存在多个连接段，仍然不允许合并
        connector = self.netiface.findConnectorByLinkIds(last_link_id, road.link.id())
        for value in self.connector_area_mapping.values():
            if connector.id() in value and len(value) >= 3:
                print(f"面域内连接段过多, 进入交叉口区域, 不再继续: {value}")
                return

        last_link = self.netiface.findLink(last_link_id)
        last_road = self.roads[last_link.id()]
        # 判断上游 link 是否有且仅有 1 个下游，且车道数与当前link一致，若一致，加入链路并继续向上游寻找
        if len(last_road.next_links) == 1 and [lane.actionType() for lane in road.link.lanes()] == [
            lane.actionType() for lane in last_road.link.lanes()]:
            if last_link in link_group:
                # link已存在，说明构成了回路，直接结束
                return
            link_group.insert(0, last_link)
            self.get_chain_by_last(last_road, link_group)
        return

    def create_new_link(self, new_link_info):
        new_link_obj = self.netiface.createLink3DWithLanePointsAndAttrs(
            new_link_info['center'],
            [
                {
                    'center': new_link_info['lanes'][k]['center'],
                    'right': new_link_info['lanes'][k]['right'],
                    'left': new_link_info['lanes'][k]['left'],
                } for k in sorted(new_link_info['lanes'])
            ],  # 必须排序
            [new_link_info['lanes'][k]['type'] for k in sorted(new_link_info['lanes'])],
            [new_link_info['lanes'][k]['attr'] for k in sorted(new_link_info['lanes'])],
            new_link_info['name']
        )
        return new_link_obj

    # 根据记录的信息 批量创建新的连接段
    def create_all_new_connector(self, old_connectors, old_new_link_mapping):
        # 如果某连接段上下游均进行了路段合并，则连接段会被重新重复创建，此处进行过滤
        exist_connector = []
        for connector in old_connectors:
            old_from_link_id = connector['from_link_id']
            old_to_link_id = connector['to_link_id']
            new_from_link_id = old_new_link_mapping[old_from_link_id][-1]  # 上游路段取新的link列表的最后一个
            new_to_link_id = old_new_link_mapping[old_to_link_id][0]  # 下游路段取新的link列表的第一个

            connector_name = f'{new_from_link_id}_{new_to_link_id}'
            if connector_name in exist_connector:
                continue
            self.netiface.createConnector3DWithPoints(new_from_link_id,
                                                      new_to_link_id,
                                                      [i[0] + 1 for i in connector['connector']],
                                                      [i[1] + 1 for i in connector['connector']],
                                                      connector['lanesWithPoints3'],
                                                      f"{new_from_link_id}-{new_to_link_id}"
                                                      )
            # 采用默认连接，防止出现连接段不平滑问题
            # netiface.createConnector(new_from_link_id, new_to_link_id, [i[0] + 1 for i in connector['connector']], [i[1] + 1 for i in connector['connector']], f"{new_from_link_id}-{new_to_link_id}")
            exist_connector.append(connector_name)


###############################################################################
# 简化路网文件所需函数


def get_section_childs(section_info: Dict, lengths: List, direction: str) -> List[Dict]:
    """
        处理某 Section 某方向的路网信息
        根据二维信息以及自定义配置，将section 进行再次处理，将宽度过窄的车道所在的路段打断，分配合适的连接段或者抹除车道
    Args:
        section_info:
        lengths: 因为分段时，以road作为最小单位，所以需要提供此 section 对应的长度断点序列
        direction: 沿参考线方向

    Returns:
        被处理后的 小路段列表
    """
    # 分为左右车道，同时过滤tess规则下不同的车道类型
    if direction == 'left':
        lane_ids = [lane_id for lane_id in section_info['lanes'].keys() if
                    lane_id > 0 and lane_id in section_info["tess_lane_ids"]]
    else:
        lane_ids = [lane_id for lane_id in section_info['lanes'].keys() if
                    lane_id < 0 and lane_id in section_info["tess_lane_ids"]]
    # 路段遍历，获取link段，处理异常点
    point_infos = []
    # 查找连接段
    for index, length in enumerate(lengths):
        point_info = {
            'lanes': {},
            'is_link': True,
        }
        for lane_id in lane_ids:
            lane_info = section_info['lanes'][lane_id]
            tess_lane_type = LANE_TYPE_MAPPING.get(lane_info['type'])
            if tess_lane_type not in WIDTH_LIMIT.keys() or lane_info['widths'][index] > \
                    WIDTH_LIMIT[tess_lane_type]['split']:
                point_info['lanes'][lane_id] = lane_info['type']  # 无宽度限制或者宽度足够，正常车道
            elif lane_info['widths'][index] > WIDTH_LIMIT[tess_lane_type]['join']:
                point_info['lanes'][lane_id] = lane_info['type']  # 宽度介于中间，作为连接段
                point_info['is_link'] = False
            # 否则，不加入车道列表
        point_infos.append(point_info)

    # 连续多个点的信息完全一致，可作为同一路段
    childs = []
    child_point = []
    start_index = None  # 分片时，start_index 为None 会视为0
    for index in range(len(lengths)):
        if len(child_point) == 1:
            start_index = index - 1
        point_info = point_infos[index]
        if index < POINT_REQUIRE:  # 首尾必须为link
            child_point.append(point_infos[0])
        elif len(lengths) - index - 1 < POINT_REQUIRE:
            child_point.append(point_infos[-1])
        elif not child_point:  # 原列表为空
            if point_info['is_link']:
                child_point.append(point_info)
            else:
                continue
        else:  # 原列表不为空
            if point_info == child_point[0]:
                child_point.append(point_info)
            elif len(child_point) >= POINT_REQUIRE:
                childs.append(
                    {
                        'start': start_index,
                        'end': index,
                        'lanes': set(child_point[0]['lanes'].keys()) & set(child_point[0]['lanes'].keys()),
                    }
                )
                child_point = []
            else:
                continue

    # 把最后一个存在的点序列导入, 最后一个应该以末尾点为准,但是如果此处包含了首&尾，应该取数据量的交集
    # 这样可能会丢失部分路段，所以在建立连接段时，必须确保 from_lane, to_lane 均存在
    childs.append(
        {
            'start': start_index,
            'end': len(lengths) - 1,
            'lanes': set(child_point[0]['lanes'].keys()) & set(child_point[0]['lanes'].keys())
        }
    )
    # lengths 只是断点序列，标记着与起始点的距离,反向用了同样的lengths
    # 得到link的列表,因为lane的点坐标与方向有关，所以此时的child已经根据方向排序
    return childs


def get_inter(string: str, roads_info: Dict) -> List:
    """
        根据 opendrive2lanelet 中定义的的车道名判断此车道的合法性，并返回相应的的 road_id,section_id,lane_id, -1
    Args:
        string: 车道名
        roads_info: 路段信息字典

    Returns:
        车道名是否合法，车道名的详细信息
    """
    inter_list = []
    is_true = True
    for i in string.split('.'):
        try:
            inter_list.append(int(i))
        except:
            inter_list.append(None)
            is_true = False

    # 检查 前后续路段 是否存在,不存在可以忽略
    if inter_list[0] not in roads_info.keys():
        is_true = False
    return [is_true, *inter_list]


def connect_childs(links: "Tessng.ILink", connector_mapping: Dict) -> None:
    """
        因为在section内对过窄车道进行了优化处理，所以可能将section切分成了多个link，需要为每个link在内部建立连接关系
    Args:
        links: section内 同方向子link 顺序列表
        connector_mapping: 全局的路段连接关系表

    Returns:
        无返回值，但路段连接关系表被扩充
    """
    for index in range(len(links) - 1):
        from_link_info = links[index]
        to_link_info = links[index + 1]
        from_link = from_link_info['link']
        to_link = to_link_info['link']
        if not (from_link and to_link and from_link_info['lane_ids'] and to_link_info['lane_ids']):
            continue

        actionTypeMapping = collections.defaultdict(lambda: {"from": set(), 'to': set()})
        for lane_id in from_link_info['lane_ids']:
            actionTypeMapping[from_link_info[lane_id].actionType()]['from'].add(lane_id)
        for lane_id in to_link_info['lane_ids']:
            actionTypeMapping[to_link_info[lane_id].actionType()]['to'].add(lane_id)

        connect_lanes = set()
        for actionType, lanes_info in actionTypeMapping.items():
            for lane_id in set(lanes_info['from'] | lanes_info['to']):
                # 车道原始编号相等，取原始编号对应的车道，否则，取临近车道(lane_ids 是有序的，所以临近车道永远偏向左边区)
                # 因为进行过自优化(人为打断与合并)，可能会导致前后失去连接关系，需要注意
                from_lane_id = min(lanes_info['from'], key=lambda x: abs(x - lane_id)) if lanes_info[
                    'from'] else None
                to_lane_id = min(lanes_info['to'], key=lambda x: abs(x - lane_id)) if lanes_info['to'] else None

                from_lane = from_link_info.get(from_lane_id)
                to_lane = to_link_info.get(to_lane_id)
                if from_lane and to_lane:
                    connect_lanes.add((from_lane.number() + 1, to_lane.number() + 1))

        if connect_lanes:
            connector_mapping[f"{from_link.id()}-{to_link.id()}"]['lFromLaneNumber'] += [i[0] for i in
                                                                                         connect_lanes]
            connector_mapping[f"{from_link.id()}-{to_link.id()}"]['lToLaneNumber'] += [i[1] for i in connect_lanes]
            connector_mapping[f"{from_link.id()}-{to_link.id()}"]['lanesWithPoints3'] += [None for _ in
                                                                                          connect_lanes]
            connector_mapping[f"{from_link.id()}-{to_link.id()}"]['infos'] += []


# 计算两向量间的夹角
def cal_angle_of_vector(v0, v1, is_use_deg=True):
    dot_product = np.dot(v0, v1)
    v0_len = np.linalg.norm(v0)
    v1_len = np.linalg.norm(v1)
    try:
        angle_rad = np.arccos(dot_product / (v0_len * v1_len))
    except ZeroDivisionError as error:
        return None

    if is_use_deg:
        return np.rad2deg(angle_rad)
    return angle_rad


# 根据前后两点坐标绘制向量
def get_vector(start_point, end_point):
    # return np.array([end_point[index] - start_point[index] for index in range(3)])
    return np.array(end_point) - np.array(start_point)


# 根据角度限制整合中心点，减少绘制路网时的点数
def get_new_point_indexs(center_points, angle):
    new_point_indexs = [0, 1]  # 前两个点是基础
    for index, point in enumerate(center_points[2:-1]):
        real_index = index + 2  # 在 center_points 中的真实索引

        point_0 = center_points[new_point_indexs[-2]]
        point_1 = center_points[new_point_indexs[-1]]
        point_2 = point

        vector_1 = get_vector(point_0, point_1)
        vector_2 = get_vector(point_0, point_2)

        included_angle = cal_angle_of_vector(vector_1, vector_2)
        point_distance = np.sqrt(np.sum((np.array(point_2) - np.array(point_1)) ** 2))

        # 如果两向量夹角变化不大，抹除观测点(不能用连续的两个点比较,即 01 对比 12，容易对缓慢变化的路段判断错误)
        # print(included_angle, angle, point_distance >= max_length, included_angle > 0)
        # print(point_0, point_1, point_2, vector_1, vector_2)
        if included_angle is None or included_angle >= angle:
            new_point_indexs.append(real_index)
        # 如果观测点距离上一点过远，且存在角度差异，也不会抹除，不加这个可能会把微小的角度误差放大到明显的地步
        elif point_distance >= max_length and included_angle > 0:
        # elif point_distance >= max_length:  # 存在微小角度偏差的路段 可能会漫延很长
            new_point_indexs.append(real_index)
        else:
            # print('不添加')
            pass
    # 最后一个点需添加
    if len(center_points) - 1 > new_point_indexs[-1]:
        new_point_indexs.append(len(center_points) - 1)

    # TODO 尝试缩减第二个点
    def is_remove_index_1(center_points, new_point_indexs):
        if len(new_point_indexs) < 3:
            # 只有两个点，无法缩减
            return False
        point_0 = center_points[new_point_indexs[0]]
        point_1 = center_points[new_point_indexs[1]]
        point_2 = center_points[new_point_indexs[2]]

        vector_1 = get_vector(point_0, point_1)
        vector_2 = get_vector(point_0, point_2)

        included_angle = cal_angle_of_vector(vector_1, vector_2)

        # 距离取较小值
        point_distance = np.sqrt(np.sum((np.array(point_1) - np.array(point_0)) ** 2))

        # 如果两向量夹角变化不大，抹除观测点(不能用连续的两个点比较,即 01 对比 12，容易对缓慢变化的路段判断错误)
        if included_angle is None or included_angle >= angle:
            return False
        # 如果观测点距离上一点过远，且存在角度差异，也不会抹除，不加这个可能会把微小的角度误差放大到明显的地步
        elif point_distance >= max_length and included_angle > 0:
            # elif point_distance >= max_length:  # 存在微小角度偏差的路段 可能会蔓延很长
            return False
        else:
            return True

    if is_remove_index_1(center_points, new_point_indexs):
        del new_point_indexs[1]
    # print(f"point 缩减 {len(center_points)} to {len(new_point_indexs)}")
    return new_point_indexs

###############################################################################

# 简化路网文件
def simplify_tessng_file(file_path, angle, length):
    """
    简化 .tess 的路网，一个纯粹的方法，不依赖于tessng
    """
    default_angle = angle
    max_length = length

    message = "路网简化结果:\n\n"
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conn = sqlite3.connect(file_path)  # 建立一个基于硬盘的数据库实例
    conn.row_factory = dict_factory

    cur = conn.cursor()  # 通过建立数据库游标对象，准备读写操作
    cur.execute("select * from link")  # 根据上表结构建立对应的表结构对象
    links = cur.fetchall()

    origin_point_counts = 0
    new_point_counts = 0
    for link in links:
        link_id = link['LinkID']
        cur.execute(
            f"select * from linkvertex join vertex on linkvertex.Vertexid=vertex.Vertexid where linkid={link_id} order by linkvertex.num")
        link_vertexs = cur.fetchall()
        center_points = [[point['X'], point['Y'], point['Z']] for point in link_vertexs]

        new_point_indexs = get_new_point_indexs(center_points, default_angle)
        if new_point_indexs[-1] != len(center_points) - 1:
            raise 1

        # 获取需要被删除的 顶点 ID
        delete_vertex_ids = []
        new_vertex_num_mapping = {}
        for index, vertex in enumerate(link_vertexs):
            if index not in new_point_indexs:
                delete_vertex_ids.append(vertex['VertexID'])
            else:
                new_vertex_num_mapping[vertex['VertexID']] = new_point_indexs.index(index) + 1

        # 判断 new_vertex_num_mapping 是否正确
        if max(new_vertex_num_mapping.values()) - min(new_vertex_num_mapping.values()) != len(
                new_vertex_num_mapping) - 1:
            raise 1

        # 先删除 link-vertex 关联表
        if len(delete_vertex_ids) == 1:
            sql = f"delete from linkvertex where linkid={link_id} and vertexid={delete_vertex_ids[0]}"
        else:
            sql = f"delete from linkvertex where linkid={link_id} and vertexid in {tuple(delete_vertex_ids)}"

        cur.execute(sql)
        # 更新 link-vertex 的 num
        for vertexid, num in new_vertex_num_mapping.items():
            sql = f'update linkvertex set num={num} where vertexid={vertexid}'
            cur.execute(sql)

        # 再删除顶点 vertex 表
        if len(delete_vertex_ids) == 1:
            sql = f"delete from vertex where vertexid={delete_vertex_ids[0]}"
        else:
            sql = f"delete from vertex where vertexid in {tuple(delete_vertex_ids)}"
        cur.execute(sql)

        # 更新路段的左右边界点
        try:
            point_count = set([len(json.loads(link[key])['data']) for key in
                               ['centerLinePointsJson', 'leftBreakPointsJson', 'rightBreakPointsJson']])
        except:
            continue

        if len(point_count) != 1:
            raise 1
        for key in ['centerLinePointsJson', 'leftBreakPointsJson', 'rightBreakPointsJson']:
            points = json.loads(link[key])['data']
            new_points = [point for index, point in enumerate(points) if index in new_point_indexs]
            sql = f'update link set {key}=:who where linkid={link_id}'
            cur.execute(sql, {"who": json.dumps({"data": new_points})})

        # 更新车道的左右边界点
        cur.execute(f"select * from lane where linkid={link_id}")
        lanes = cur.fetchall()

        for lane in lanes:
            lane_id = lane["LaneID"]
            point_count = set([len(json.loads(lane[key])['data']) for key in
                               ['centerLinePointsJson', 'leftBreakPointsJson', 'rightBreakPointsJson']])
            if len(point_count) != 1:
                raise 1

            for key in ['centerLinePointsJson', 'leftBreakPointsJson', 'rightBreakPointsJson']:
                points = json.loads(lane[key])['data']
                new_points = [point for index, point in enumerate(points) if index in new_point_indexs]
                sql = f'update lane set {key}=:who where laneid={lane_id}'
                cur.execute(sql, {"who": json.dumps({"data": new_points})})

        origin_point_counts += len(center_points)
        new_point_counts += len(new_point_indexs)

    message += f"原路段中可查询的点位共 {origin_point_counts} 个, 简化后剩余 {new_point_counts} 个, \n"

    cur.execute("select * from laneconnector")  # 根据上表结构建立对应的表结构对象
    laneconnectors = cur.fetchall()
    origin_point_counts = 0
    new_point_counts = 0
    for laneconnector in laneconnectors:
        lane = laneconnector
        points = json.loads(lane["centerLinePointsJson"])
        if not points:
            continue

        points = points['data']
        center_points = [[point['x'], point['y'], point['z']] for point in points]
        new_point_indexs = get_new_point_indexs(center_points, default_angle)

        for key in ['centerLinePointsJson', 'leftBreakPointsJson', 'rightBreakPointsJson']:
            points = json.loads(lane[key])['data']
            new_points = [point for index, point in enumerate(points) if index in new_point_indexs]
            sql = f'update laneconnector set {key}=:who where connID={laneconnector["connID"]} and startLaneid={laneconnector["StartLaneID"]} and endlaneid={laneconnector["EndLaneID"]}'
            cur.execute(sql, {"who": json.dumps({"data": new_points})})

        origin_point_counts += len(points)
        new_point_counts += len(new_points)

    message += f"原连接段中可查询的点位共 {origin_point_counts} 个, 简化后剩余 {new_point_counts} 个 \n"

    conn.commit()  # 保存提交，确保数据保存成功
    conn.close()  # 关闭与数据库的连接

    return message