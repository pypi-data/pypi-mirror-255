import json
from pyproj import Proj
from PySide2.QtCore import QObject, Signal

from ..DLLs.Tessng import PyCustomerSimulator, tessngIFace, p2m
from ..Toolbox.traj_output.get_traj_data import get_traj_data
from ..Toolbox.traj_output.send_traj_data import SendData
from ..Tessng.MyMenu import GlobalVar


class MySimulator(QObject, PyCustomerSimulator):
    signalRunInfo = Signal(str)
    forStopSimu = Signal()
    forReStartSimu = Signal()

    def __init__(self):
        QObject.__init__(self)
        PyCustomerSimulator.__init__(self)

        # 投影关系
        self.traj_proj = None
        # move
        self.traj_move = None
        # 数据发送线程
        self.send_data_class = None

    # 仿真开始前
    def beforeStart(self, ref_keepOn):
        traj_proj_string = GlobalVar.traj_proj_string # str
        traj_json_config = GlobalVar.traj_json_config # str
        traj_kafka_config = GlobalVar.traj_kafka_config # dict

        # 投影关系
        if GlobalVar.traj_proj_string:
            self.traj_proj = Proj(traj_proj_string)
        else:
            self.traj_proj = lambda x,y,inverse=None: (None,None)

        # move
        iface = tessngIFace()
        netiface = iface.netInterface()
        move = netiface.netAttrs().otherAttrs().get("move_distance")
        if move is None or "tmerc" in traj_proj_string:
            self.traj_move = {"x_move": 0, "y_move": 0}
        else:
            self.traj_move = {"x_move": -move["x_move"], "y_move": -move["y_move"]}

        # 数据发送线程
        if traj_json_config or traj_kafka_config:
            self.send_data_class = SendData(traj_json_config, traj_kafka_config)

    # 仿真结束后
    def afterStop(self):
        # 投影关系
        self.traj_proj = None

        # move
        self.traj_move = None

        # 数据发送进程
        if self.send_data_class is not None:
            self.send_data_class.close()
            self.send_data_class = None

    # 每帧仿真后
    def afterOneStep(self):
        iface = tessngIFace()
        simuiface = iface.simuInterface()

        # 如果不需要导出，就不需要计算
        if self.send_data_class is None:
            return

        # 计算轨迹数据
        traj_data = get_traj_data(simuiface, self.traj_proj, p2m, self.traj_move)

        # 发送轨迹数据
        self.send_data_class.put_data(traj_data)

