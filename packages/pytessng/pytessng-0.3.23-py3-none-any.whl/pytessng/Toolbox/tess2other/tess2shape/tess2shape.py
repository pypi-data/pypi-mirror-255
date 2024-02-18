import os
import json
from .utils import config


def tess2shape(netiface, params, mode):
    # params:
    # - file_path
    # - proj_string

    # 文件保存路径
    file_path = params["file_path"]
    
    # 场景比例尺
    config.sceneScale = netiface.sceneScale()
    
    # 导入计算模块
    from .utils.get_data import get_info

    # 获取数据
    lane_gdf, connector_gdf = get_info(netiface, params["proj_string"])
    
    # 写入数据
    if mode == "shape":
        # 创建文件夹
        os.makedirs(file_path, exist_ok=True)
        # 写入数据
        lane_gdf.to_file(os.path.join(file_path, "lane.shp"))
        if connector_gdf is not None:
            connector_gdf.to_file(os.path.join(file_path, "laneConnector.shp"))
    elif mode == "geojson":
        lane_geojson = json.loads(lane_gdf.to_json())
        # 将车道的type改为lane
        for i in range(len(lane_geojson["features"])):
            lane_geojson["features"][i]["type"] = "lane"
        # 将车道连接的type改为laneConnector
        if connector_gdf is not None:
            connector_geojson = json.loads(connector_gdf.to_json())
            for i in range(len(connector_geojson["features"])):
                connector_geojson["features"][i]["type"] = "laneConnector"
            lane_geojson["features"].extend(connector_geojson["features"])
        # 写入数据
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(lane_geojson, json_file, indent = 4, ensure_ascii=False)
