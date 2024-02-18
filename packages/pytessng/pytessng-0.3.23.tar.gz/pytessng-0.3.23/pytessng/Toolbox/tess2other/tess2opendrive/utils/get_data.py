from xml.dom import minidom
from . import config
from .node import Doc
from .models import Junction, Connector, Road
from .....Tessng.MyMenu import ProgressDialog as pgd


def get_data(netiface, proj_string:str):
    # move
    move = netiface.netAttrs().otherAttrs().get("move_distance")
    if not move or "tmerc" in proj_string:
        config.x_move = 0
        config.y_move = 0
    else:
        config.x_move = -move["x_move"]
        config.y_move = -move["y_move"]

    # 遍历连接段
    connectors = []
    junctions = []
    areas = netiface.allConnectorArea()
    for ConnectorArea in pgd.progress(areas, '连接段数据保存中（1/2）'):
        junction = Junction(ConnectorArea)
        junctions.append(junction)
        for connector in ConnectorArea.allConnector():
            # 为所有的车道连接创建独立的 road，关联至 junction
            for laneConnector in connector.laneConnectors():
                connectors.append(Connector(laneConnector, junction))

    # 遍历路段
    roads = []
    links = netiface.links()
    for link in pgd.progress(links, '路段数据保存中（2/2）'):
        roads.append(Road(link))

    # 路网绘制成功后，写入xodr文件
    doc = Doc()
    # 如果有投影中心的信息
    if proj_string:
        doc.init_doc(proj_string=proj_string)
    else:
        doc.init_doc()
    doc.add_junction(junctions)
    doc.add_road(roads + connectors)

    uglyxml = doc.doc.toxml()
    xml = minidom.parseString(uglyxml)
    xml_pretty_str = xml.toprettyxml()
    
    return xml_pretty_str