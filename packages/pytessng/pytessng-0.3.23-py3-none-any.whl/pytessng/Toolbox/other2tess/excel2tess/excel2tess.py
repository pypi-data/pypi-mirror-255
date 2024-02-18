from .utils import config


def excel2tess(netiface, params):
    # params:
    # - file_path
    
    file_path = params["file_path"]
    
    config.sceneScale = netiface.sceneScale()
    
    from .utils.get_data import get_data
    from .utils.create_network import create_network
    
    # 读取数据
    links_data, other_data = get_data(file_path) # dict, dict

    # 创建路段和连接段
    if links_data:
        create_network(netiface, links_data, other_data)
        status, message = True, None
    else:
        status, message = False, "所选文件中无数据或无合法数据"

    return status, message


