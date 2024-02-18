import traceback
from .config import LANE_TYPE_MAPPING
from .functions import get_coo_list
from .....Tessng.MyMenu import Logger
from .....Tessng.MyMenu import ProgressDialog as pgd


def create_network(netiface, links_info, connectors_info, other_info):
    netiface.setNetAttrs("Shapefile Network", otherAttrsJson=other_info)

    error_links = []
    error_connectors = []
    
    # 创建路段
    for road_id in pgd.progress(links_info, "创建路段中（7/8）"):
        link_info = links_info[road_id]
        link_type = []
        
        # 获取车道点位
        lanesWithPoints = []
        for lane_id, lane in link_info["lanes_data"].items():
            points = lane["points"]
            lane_type = LANE_TYPE_MAPPING.get(lane["type"], '机动车道')
            link_type.append(lane_type)
            try:
                lanesWithPoints.append({
                    'left': get_coo_list(points['left']),
                    'center': get_coo_list(points['center']),
                    'right': get_coo_list(points['right']),
                })
            except Exception as e:
                error_links.append(f"{road_id}-{lane_id}")
                Logger.logger_network.error(traceback.format_exc())
                continue
        
        # 获取路段点位
        # 如果是奇数，取中间车道的中心线
        laneCount = len(lanesWithPoints)
        if laneCount % 2 == 1:
            lCenterLinePoint = lanesWithPoints[int((laneCount-1)/2)]["center"]
        # 如果是偶数，取中间两车道的边线
        else:
            lCenterLinePoint = lanesWithPoints[int(laneCount/2)]["right"]
        
        # 创建路段及车道
        link_obj = netiface.createLink3DWithLanePoints(lCenterLinePoint, lanesWithPoints)
        if link_obj:
            link_obj.setName(f"shp_road_id: {road_id}")
            link_obj.setLaneTypes(link_type)
            links_info[road_id]['obj'] = link_obj
        else:
            error_links.append(f"{road_id}-all")
        
    # 创建连接段
    for connector_road_tuple, connector_info in pgd.progress(connectors_info.items(), "创建连接段中（8/8）"):
        from_link = links_info[connector_road_tuple[0]]['obj']
        to_link = links_info[connector_road_tuple[1]]['obj']
        
        from_link_id, to_link_id = from_link.id(), to_link.id()
        
        from_lane_numbers, to_lane_numbers, lanesWithPoints3 = [], [], []
        for connector in connector_info:
            from_lane_numbers.append(connector['from_lane_number'])
            to_lane_numbers.append(connector['to_lane_number'])
            if connector.get('points'):
                points = connector['points']
                lanesWithPoints3.append(
                    {
                        "center": get_coo_list(points['center']),
                        "left": get_coo_list(points['left']),
                        "right": get_coo_list(points['right']),
                    }
                )

        try:
            if all(lanesWithPoints3):
                netiface.createConnector3DWithPoints(from_link_id, to_link_id, from_lane_numbers, to_lane_numbers,
                                                     lanesWithPoints3, f"{from_link_id}-{to_link_id}")
            else:
                netiface.createConnector(from_link_id, to_link_id, from_lane_numbers, to_lane_numbers)
        except:
            Logger.logger_network.error(traceback.format_exc())
            error_connectors.append(connector_road_tuple)

    # 路段创建信息
    if error_links:
        link_message = f"{len(error_links)} out of {len(links_info)} links failed to be created."
    else:
        link_message = "All links created successfully."
    Logger.logger_network.info(link_message)

    # 连接段创建信息
    if error_connectors:
        connector_message = f"{len(error_connectors)} out of {len(connectors_info)} connectors failed to be created."
    else:
        connector_message = "All connectors created successfully."
    Logger.logger_network.info(connector_message)
