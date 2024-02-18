import json
from .utils import config


def tess2json(netiface, params):
    # params: 参数
    # - file_path
    # - proj_string
    
    # 文件保存路径
    file_path = params["file_path"]
    
    # 场景比例尺
    config.sceneScale = netiface.sceneScale()
    
    # 导入计算模块
    from .utils.get_data import get_data
    
    # 获取数据
    json_data = get_data(netiface, params["proj_string"])
    
    # 写入数据
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)
