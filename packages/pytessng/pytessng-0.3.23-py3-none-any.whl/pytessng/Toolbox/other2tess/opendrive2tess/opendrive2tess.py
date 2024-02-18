from lxml import etree

from .utils import config


def opendrive2tess(netiface, params):
    # params:
    # - file_path
    # - step_length
    # - lane_types
    
    file_path = params["file_path"]
    step_length = params["step_length"]
    lane_types = params["lane_types"]
    
    config.sceneScale = netiface.sceneScale()

    from .opendrive2lanelet.opendriveparser.parser import parse_opendrive
    from .utils.network_utils import Network
    
    with open(file_path, "r", encoding='utf-8') as file_in:
        root_node = etree.parse(file_in).getroot()
        opendrive = parse_opendrive(root_node)
    
    network = Network(opendrive)
    network.convert_network(step_length)
    error_junction = network.create_network(lane_types, netiface)

    # 错误信息
    if error_junction:
        print("error_junction:", error_junction)

    return True, None

