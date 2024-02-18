from pyproj import Proj
from geopandas import GeoDataFrame
from shapely.geometry import LineString
from . import config
from .functions import p2m, qtpoint2point, point2latlon
from .....Tessng.MyMenu import ProgressDialog as pgd


def get_info(netiface, proj_string=""):
    lane_action_type = config.lane_action_type

    # 有投影就转为经纬度，否则就用X/Y
    if proj_string:
        projection = Proj(proj_string)
    else:
        projection = None
    # move
    move_distance = netiface.netAttrs().otherAttrs().get("move_distance")
    if move_distance is None or "tmerc" in proj_string:
        move = {"x_move": 0, "y_move": 0}
    else:
        move = move_distance

    # 创建路段的 GeoDataFrame 保存路段信息
    links = netiface.links()
    lane_features = []
    for link in pgd.progress(links, '路段数据保存中（1/2）'):
        link_id = link.id()
        for lane in link.lanes():
            lane_id = lane.id()
            lane_number = lane.number() + 1
            lane_type = lane_action_type.get(lane.actionType(), "driving")
            lane_width = p2m(lane.width())
            lane_points = qtpoint2point(lane.centerBreakPoint3Ds(), move=move)
            if proj_string:
                lane_points = point2latlon(lane_points, projection)
            feature = {
                'id': lane_id,
                'roadId': link_id,
                'laneNumber': lane_number,
                'type': lane_type,
                'width': lane_width,
                'geometry': LineString(lane_points)
            }
            lane_features.append(feature)
    lane_gdf = GeoDataFrame(lane_features, crs=proj_string)

    # 创建连接段的 GeoDataFrame 保存连接段信息
    connectors = netiface.connectors()
    if connectors:
        connector_features = []
        for connector in pgd.progress(connectors, '连接段数据保存中（2/2）'):
            for lane_connector in connector.laneConnectors():
                from_lane_id = lane_connector.fromLane().id()
                to_lane_id = lane_connector.toLane().id()
                lane_points = qtpoint2point(lane_connector.centerBreakPoint3Ds(), move=move)
                if proj_string:
                    lane_points = point2latlon(lane_points, projection)
                feature = {
                    'preLaneId': from_lane_id,
                    'sucLaneId': to_lane_id,
                    'geometry': LineString(lane_points)
                }
                connector_features.append(feature)
        connector_gdf = GeoDataFrame(connector_features, crs=proj_string)
    else:
        connector_gdf = None
    
    return lane_gdf, connector_gdf
