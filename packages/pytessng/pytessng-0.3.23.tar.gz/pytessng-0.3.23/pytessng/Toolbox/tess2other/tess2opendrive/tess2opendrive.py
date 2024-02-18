from .utils import config


def tess2opendrive(netiface, params):
    # params:
    # - file_path
    # - proj_string
    
    # 文件保存路径
    file_path = params["file_path"]
    
    # 场景比例尺
    config.sceneScale = netiface.sceneScale()
    
    # 导入计算模块
    from .utils.get_data import get_data
    
    # 获取数据
    xml_pretty_str = get_data(netiface, params["proj_string"])
    
    # 写入数据
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(xml_pretty_str)