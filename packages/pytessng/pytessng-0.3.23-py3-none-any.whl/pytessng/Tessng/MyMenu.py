import os
import shutil
import uuid
import logging
import traceback
from datetime import datetime
from subprocess import Popen as open_folder
from functools import partial, reduce
from ipaddress import ip_address
from warnings import filterwarnings
from requests import post
from PySide2.QtWidgets import QWidget, QMenu, QAction, QLabel, QLineEdit, QTextEdit
from PySide2.QtWidgets import QComboBox, QRadioButton, QCheckBox, QPushButton
from PySide2.QtWidgets import QFileDialog, QMessageBox, QProgressDialog
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox, QButtonGroup
from PySide2.QtCore import QPointF, Qt, QRegExp, QCoreApplication
from PySide2.QtGui import QIcon, QIntValidator, QDoubleValidator, QRegExpValidator
from pyautogui import size as scene_size
from webbrowser import open as open_file
from kafka import KafkaProducer
from kafka import KafkaConsumer

from ..DLLs.Tessng import tessngIFace, m2p
from ..Toolbox.other2tess.other2tess import other2tess
from ..Toolbox.tess2other.tess2other import tess2other
from ..Toolbox.link_edit import link_edit

# 忽略警告
filterwarnings("ignore")


# 全局变量类
class GlobalVar():
    # 是否需要打断路段
    is_need_split_link = False
    # 打断路段的action
    action_split_link = None
    # 路段颜色
    link_color = None

    # 车辆轨迹的投影
    traj_proj_string = ""
    # 车辆轨迹保存为JSON文件路径
    traj_json_config = None
    # 车辆轨迹上传至kafka的配置
    traj_kafka_config = None


# 通用函数类
class Tools():
    # 进程(工作空间)的路径
    workspace_path = os.path.join(os.getcwd(), "WorkSpace")
    # 文件所在文件夹的路径
    this_file_path = os.path.dirname(__file__)

    # (1) UUID的路径
    uuid_path = os.path.join(os.environ['USERPROFILE'], ".pytessng")
    # (2) ico图标的路径
    icon_path = os.path.join(os.path.dirname(this_file_path), "Files", "Ico", "TESSNG.ico")
    # (3) 说明书的路径
    instruction_path = os.path.join(os.path.dirname(this_file_path), "Files", "Doc", "用户使用手册.pdf")
    # (4) 样例文件的路径
    examples_path = "file:\\" + os.path.join(workspace_path, "Examples")
    # (5) 日志文件的路径
    log_path = os.path.join(workspace_path, "Log")
    # (6) 默认创建路网打开文件和导出路网保存数据的路径
    default_network_path = os.path.join(workspace_path, "Examples")  # 样例文件夹
    # (7) 导出轨迹保存为Json的路径
    default_traj_json_path = os.path.join(workspace_path, "Data", "traj_data")
    # (8) osm数据保存的路径
    osm_path = os.path.join(workspace_path, "Data", "osm_data")

    # 获取电脑屏幕的尺寸
    screen_width, screen_height = scene_size()

    # 设置面板的各属性
    @staticmethod
    def set_attribution(widget):
        # 设置名称
        widget.setWindowTitle(widget.name)
        # 设置图标
        widget.setWindowIcon(QIcon(Tools.icon_path))
        # 设置位置和尺寸
        x = (Tools.screen_width - widget.size().width()) // 2
        y = (Tools.screen_height - widget.size().height()) // 2
        widget.setGeometry(x, y, widget.width, widget.height)
        # 设置尺寸固定
        # widget.setFixedSize(widget.width, widget.height)
        # 设置窗口标志位，使其永远在最前面
        widget.setWindowFlags(widget.windowFlags() | Qt.WindowStaysOnTopHint)

    # 读取.tess文件的属性
    @staticmethod
    def read_file_proj():
        iface = tessngIFace()
        netiface = iface.netInterface()
        attrs = netiface.netAttrs().otherAttrs()
        if attrs.get("proj_string"):
            proj_string = attrs["proj_string"]
            info = proj_string
        else:
            proj_string = ""
            info = "（未在TESS文件中读取到投影信息）"
        return proj_string, info

    # 读取.tess文件的名称
    @staticmethod
    def read_file_name():
        iface = tessngIFace()
        tmpNetPath = iface.netInterface().netFilePath()
        base_name = os.path.basename(tmpNetPath)
        file_name, _ = os.path.splitext(base_name)
        return file_name

    # 获取打开文件的路径
    @staticmethod
    def open_file(formats):
        # 指定文件后缀
        xodrSuffix = ";;".join([f"{format} Files (*.{suffix})" for format, suffix in formats])
        # 默认读取位置
        dbDir = Tools.default_network_path
        # 弹出文件选择框
        file_path, filtr = QFileDialog.getOpenFileName(None, "打开文件", dbDir, xodrSuffix)
        return file_path

    # 获取打开文件夹的路径
    @staticmethod
    def open_folder():
        # 默认读取位置
        dbDir = Tools.default_network_path
        # 弹出文件选择框
        folder_path = QFileDialog.getExistingDirectory(None, "打开文件夹", dbDir)
        return folder_path

    # 选择保存文件路径
    @staticmethod
    def save_file(format):
        # 指定文件后缀
        xodrSuffix = f"{format[0]} Files (*.{format[1]})"
        # 默认保存位置是路径+文件名称
        dbDir = os.path.join(Tools.default_network_path, Tools.read_file_name())
        # 弹出文件选择框
        file_path, filtr = QFileDialog.getSaveFileName(None, "保存文件", dbDir, xodrSuffix)
        return file_path

    # 弹出警告或提示提示框
    @staticmethod
    def show_info_box(content, mode="info"):
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon(Tools.icon_path))
        if mode == "warning":
            msg_box.setWindowTitle("警告")
            msg_box.setIcon(QMessageBox.Warning)
        else:
            msg_box.setWindowTitle("提示")
            msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(content)
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)  # 设置窗口标志，使其显示在最前面
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    # 确认弹窗
    @staticmethod
    def show_confirm_dialog(messages):
        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon(Tools.icon_path))
        msg_box.setWindowTitle(messages["title"])
        msg_box.setText(messages["content"])

        # 设置按钮
        if messages.get("no"):
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            msg_box.button(QMessageBox.No).setText(messages["no"])
        else:
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        # 设置窗口标志，使其显示在最前面
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
        # 设置默认选项
        msg_box.setDefaultButton(QMessageBox.Cancel)
        # 修改按钮上的文本
        msg_box.button(QMessageBox.Yes).setText(messages["yes"])
        msg_box.button(QMessageBox.Cancel).setText("取消")
        # 获取选择结果
        result = msg_box.exec_()

        return result

    # 路网创建
    @staticmethod
    def network_import(widget, params):
        iface = tessngIFace()
        netiface = iface.netInterface()
        simuiface = iface.simuInterface()
        guiiface = iface.guiInterface()

        # 1.更改默认路径
        path = params.get("folder_path") or params.get("file_path") or params.get("osm_file_path")
        if path:
            Tools.default_network_path = os.path.dirname(path)

        # 2.正在仿真中无法导入
        if iface.simuInterface().isRunning() or iface.simuInterface().isPausing():
            Tools.show_info_box("请先停止仿真！", "warning")
            return

        # 3.路网上已经有路段进行询问
        link_count = netiface.linkCount()
        if link_count > 0:
            messages = {
                "title": "是否继续",
                "content": "路网上已有路段，请选择是否继续导入",
                "yes": "继续",
            }
            confirm = Tools.show_confirm_dialog(messages)
            if confirm != QMessageBox.Yes:
                return

        # 4.尝试关闭在线地图
        win = guiiface.mainWindow()
        win.showOsmInline(False)

        # 5.关闭窗口
        widget.close()

        # 6.执行转换
        GlobalVar.link_color = None
        try:
            # 当前路网上的路段ID
            current_linkIds = netiface.linkIds()
            # 创建路段
            Logger.logger_network.info(f"Import mode: {widget.mode}")
            Logger.logger_network.info(params)
            status, message = other2tess(netiface, params, widget.mode)
            # 如果有问题
            if not status:
                info, mode = message, "warning"
            # 如果没问题，问要不要移动
            else:
                # 新创建的路段
                new_links = [link for link in netiface.links() if link.id() not in current_linkIds]
                xs, ys = [], []
                for link in new_links:
                    points = link.centerBreakPoints()
                    xs.extend([point.x() for point in points])
                    ys.extend([point.y() for point in points])
                x_min, x_max = min(xs), max(xs)
                y_min, y_max = min(ys), max(ys)
                message = f"新创建路网的范围：\n    x = [ {x_min:.1f} m , {x_max:.1f} m ]\n    y = [ {y_min:.1f} m , {y_max:.1f} m ]\n"

                # osm自动移动，其他要询问
                if widget.mode != "osm":
                    messages = {
                        "title": "是否移动至中心",
                        "content": message + "是否将路网移动到场景中心",
                        "yes": "确定",
                    }
                    confirm = Tools.show_confirm_dialog(messages)

                    # 移动
                    attrs = netiface.netAttrs().otherAttrs()
                    if confirm == QMessageBox.Yes:
                        move = QPointF(m2p(attrs["move_distance"]["x_move"]), -m2p(attrs["move_distance"]["y_move"]))
                        netiface.moveLinks(new_links, move)
                    # 不移动
                    else:
                        attrs.update({"move_distance": {"x_move": 0, "y_move": 0}})
                        netiface.setNetAttrs("Excel Network", otherAttrsJson=attrs)

                info, mode = "导入成功", "info"
            Logger.logger_network.info(netiface.netAttrs().otherAttrs())
        except:
            info, mode = "导入失败", "warning"
            Logger.logger_network.error(traceback.format_exc())

        # 7.设置场景宽度和高度
        all_links = netiface.links()
        if all_links:
            xs, ys = [], []
            for link in all_links:
                points = link.centerBreakPoints()
                xs.extend([point.x() for point in points])
                ys.extend([point.y() for point in points])
            width = max(max(abs(max(xs)), abs(min(xs))) * 2 + 10, 600)
            height = max(max(abs(max(ys)), abs(min(ys))) * 2 + 10, 400)
            netiface.setSceneSize(width, height)  # (m)

        # 8.设置不限时长
        simuiface.setSimuIntervalScheming(0)

        # 9.关闭进度条
        ProgressDialog().close()

        # 10.打印属性信息
        attrs = netiface.netAttrs().otherAttrs()
        print("=" * 66)
        print("Create network! Network attrs:")
        for k, v in attrs.items():
            print(f"\t{k:<15}:{' '*5}{v}")
        print("=" * 66, "\n")

        # 11.弹出提示框
        Tools.show_info_box(info, mode)

        # 12.记录信息
        Tools.send_message("operation", widget.name)

    # 路网导出
    @staticmethod
    def network_export(widget):
        iface = tessngIFace()
        netiface = iface.netInterface()
        simuiface = iface.simuInterface()

        # 1.正在仿真中无法导出
        if simuiface.isRunning() or simuiface.isPausing():
            Tools.show_info_box("请先停止仿真！", "warning")
            return

        # 2.检查路网上是否有路段
        if netiface.linkCount() == 0:
            Tools.show_info_box("当前路网没有路段 !", "warning")
            return

        # 3.获取投影
        if hasattr(widget, 'checkBox'):
            isChecked = widget.checkBox.isChecked()
        elif hasattr(widget, 'radio_coord_2'):
            isChecked = widget.radio_coord_2.isChecked()
        else:
            isChecked = False
        if isChecked:
            if widget.radio_proj_custom.isChecked():
                lon_0 = float(widget.lineEdit_proj_custom_lon.text())
                lat_0 = float(widget.lineEdit_proj_custom_lat.text())
                proj_string = f'+proj=tmerc +lon_0={lon_0} +lat_0={lat_0} +ellps=WGS84'
            else:
                proj_string = widget.file_proj_string
        else:
            proj_string = ""

        # 4.获取保存路径
        file_path = Tools.save_file(widget.format)
        if not file_path:
            return
        # 更改默认路径
        Tools.default_network_path = os.path.dirname(file_path)

        # 5.关闭窗口
        widget.close()

        # 6.执行转换
        Logger.logger_network.info(f"EXport mode: {widget.mode}")
        Logger.logger_network.info(netiface.netAttrs().otherAttrs())
        params = {"proj_string": proj_string, "file_path": file_path}
        Logger.logger_network.info(params)
        tess2other(netiface, params, widget.mode)

        # 7.关闭进度条
        ProgressDialog().close()

        # 8.提示信息
        Tools.show_info_box("保存成功！")

        # 9.记录信息
        Tools.send_message("operation", widget.name)

    @staticmethod
    def setup_logger(name, level=logging.INFO):
        format_string = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        save_log_path = Tools.log_path
        current_date = datetime.now().strftime('%Y%m%d')
        save_log_file_path = f"{save_log_path}\\{name}_{current_date}.log"

        # 创建日志记录器对象
        logger = logging.getLogger(name)

        # 清空已存在的处理程序和过滤器，以防止重复添加
        logger.handlers = []
        logger.filters = []

        # 确保文件夹存在
        os.makedirs(save_log_path, exist_ok=True)
        # 创建一个文件处理程序
        file_handler = logging.FileHandler(save_log_file_path)  # 输出到文件
        file_handler.setLevel(level)  # 设置文件处理程序的日志级别

        # 创建一个控制台处理程序
        console_handler = logging.StreamHandler()  # 输出到控制台
        console_handler.setLevel(level)  # 设置控制台处理程序的日志级别

        # 创建一个格式化器，定义日志信息格式
        formatter = logging.Formatter(format_string)

        # 设置格式化器
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 将文件处理程序和控制台处理程序添加到日志记录器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # 设置记录器的级别为INFO
        logger.setLevel(level)

        return logger

    # 发送信息
    @staticmethod
    def send_message(path, message):
        # 用于唯一标识
        uuid_path = Tools.uuid_path
        if os.path.exists(uuid_path):
            UUID = open(uuid_path, "r").read()
        else:
            UUID = str(uuid.uuid4())
            with open(uuid_path, "w") as f:
                f.write(UUID)

        ip = u"\u0031\u0032\u0039\u002e\u0032\u0031\u0031\u002e\u0032\u0038\u002e\u0032\u0033\u0037"
        port = u"\u0035\u0036\u0037\u0038"
        url = f"http://{ip}:{port}/{path}/"
        message = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user": os.getlogin(),
            "UUID": UUID,
            "message": message,
        }
        try:
            status_code = post(url, json=message).status_code
        except:
            status_code = 502
        return status_code


# 进度条类
class ProgressDialog(QProgressDialog):
    _instance = None
    _init = False
    def __new__(cls,):
        if ProgressDialog._instance is None:
            ProgressDialog._instance = super().__new__(cls)
        return ProgressDialog._instance

    def __init__(self):
        if ProgressDialog._init:
            return
        ProgressDialog._init = True

        super(ProgressDialog, self).__init__()
        self.setWindowTitle('进度条')
        self.setWindowIcon(QIcon(Tools.icon_path))
        self.setCancelButton(None)  # 禁用取消按钮
        self.setRange(0, 100+1)
        self.setValue(0)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)  # 设置窗口显示在最上面
        self.setFixedWidth(400)

    # 更新进度条
    def update_progress(self, index, all_count, new_text=""):
        self.setLabelText(new_text)
        new_value = int(round(index / all_count * 100, 0))
        self.setValue(new_value)
        self.show()
        # 立刻更新界面
        QCoreApplication.processEvents()

    # 包裹器
    @staticmethod
    def progress(iterable_items, text=""):
        iterable_items_list = list(iterable_items)
        all_count = len(iterable_items_list)
        ProgressDialog().setValue(0)
        for index, item in enumerate(iterable_items_list):
            yield item
            ProgressDialog().update_progress(index + 1, all_count, text)
        ProgressDialog().hide()


# 日志类
class Logger:
    logger_network = Tools.setup_logger("network")


# 菜单栏类
class MyMenu(QMenu):
    def __init__(self, *args, extension=False):
        super().__init__(*args)
        # 是否功能拓展
        self.extension = extension

        # 初始化
        self.init()

    def init(self):
        self.setObjectName("PyTessng")
        self.setTitle("路网编辑")

        # 1.路网创建
        self.menu_network_import = self.addMenu('路网创建')
        # 1.1.导入OpenDrive
        self.action_network_import_opendrive = self.menu_network_import.addAction('导入OpenDrive (.xodr)')
        self.action_network_import_opendrive.triggered.connect(self.network_import_opendrive)
        # 1.2.导入Shape
        self.action_network_import_shape = self.menu_network_import.addAction('导入Shape')
        self.action_network_import_shape.triggered.connect(self.network_import_shape)
        # 1.3.导入OpenStreetMap
        self.action_network_import_openstreetmap = self.menu_network_import.addAction('导入OpenStreetMap')
        self.action_network_import_openstreetmap.triggered.connect(self.network_import_openstreetmap)
        # 1.4.导入Excel
        self.action_network_import_excel = self.menu_network_import.addAction('导入Excel (.xlsx/.xls/.csv)')
        self.action_network_import_excel.triggered.connect(self.network_import_excel)

        # 2.路网数据导出
        self.menu_network_export = self.addMenu('路网数据导出')
        # 2.1.导出OpenDrive
        self.action_network_export_opendrive = self.menu_network_export.addAction('导出为OpenDrive (.xodr)')
        self.action_network_export_opendrive.triggered.connect(self.network_export_opendrive)
        # 2.2.导出Shape
        self.action_network_export_shape = self.menu_network_export.addAction('导出为Shape')
        self.action_network_export_shape.triggered.connect(self.network_export_shape)
        # 2.3.导出GeoJson
        self.action_network_export_geojson = self.menu_network_export.addAction('导出为GeoJson')
        self.action_network_export_geojson.triggered.connect(self.network_export_geojson)

        if self.extension:
            # 2.4.导出Unity
            self.action_network_export_unity = self.menu_network_export.addAction('导出为Unity (.json)')
            self.action_network_export_unity.triggered.connect(self.network_export_unity)
            # 2.5.导出Json
            self.action_network_export_json = self.menu_network_export.addAction('导出为Json')
            self.action_network_export_json.triggered.connect(self.network_export_json)

        # 3.路网编辑
        self.menu_network_edit = self.addMenu('路段编辑')
        if self.extension:
            # 3.1.创建路段
            self.action_network_edit_create = self.menu_network_edit.addAction('创建路段')
            self.action_network_edit_create.triggered.connect(self.network_edit_create)
            # 3.2.打断路段
            self.action_network_edit_split = QAction("打断路段")
            self.action_network_edit_split.setCheckable(True)
            self.menu_network_edit.addAction(self.action_network_edit_split)
            self.action_network_edit_split.triggered.connect(self.network_edit_split)
            self.action_network_edit_split.setEnabled(False)
            GlobalVar.action_split_link = self.action_network_edit_split # TODO 两种方式重复
        else:
            self.action_network_edit_split = None

        # 3.3.合并路段
        self.action_network_edit_connect = self.menu_network_edit.addAction('合并路段')
        self.action_network_edit_connect.triggered.connect(self.network_edit_connect)
        # 3.4.简化路网
        self.action_network_edit_simplify = self.menu_network_edit.addAction('简化路网')
        self.action_network_edit_simplify.triggered.connect(self.network_edit_simplify)

        # 4.轨迹导出
        self.action_trajectory_export = QAction("轨迹数据导出")
        self.addAction(self.action_trajectory_export)
        self.action_trajectory_export.triggered.connect(self.trajectory_export)
        self.action_trajectory_export.setEnabled(False)

        # 5.更多
        self.menu_more = self.addMenu('更多')
        # 5.1.打开说明书
        self.action_open_instruction = self.menu_more.addAction("打开说明书")
        self.action_open_instruction.triggered.connect(partial(self.open_instruction))
        # 5.2.打开样例
        self.action_open_examples = self.menu_more.addAction("打开路网创建样例")
        self.action_open_examples.triggered.connect(partial(self.open_examples))
        # 5.3.提出建议
        self.action_send_advise = self.menu_more.addAction("提交用户反馈")
        self.action_send_advise.triggered.connect(partial(self.send_advise))

        iface = tessngIFace()
        win = iface.guiInterface().mainWindow()
        # 关联槽函数
        win.forPythonOsmInfo.connect(NetworkImportOpenstreetmap.create_network_online)
        # 关闭osm在线地图
        win.showOsmInline(False)

        # 统计用户数量
        Tools.send_message("operation", "visit")

    # 1.1.导入OpenDrive
    def network_import_opendrive(self):
        self.dialog_network_import_opendrive = NetworkImportOpendrive()
        self.dialog_network_import_opendrive.show()

    # 1.2.导入Shape
    def network_import_shape(self):
        self.dialog_network_import_shape = NetworkImportShape()
        self.dialog_network_import_shape.show()

    # 1.3.导入OpenStreetMap
    def network_import_openstreetmap(self):
        messages = {
            "title": "OSM导入模式",
            "content": "请选择导入离线文件或获取在线地图",
            "yes": "导入离线文件",
            "no": "获取在线地图",
        }
        result = Tools.show_confirm_dialog(messages)

        if result == QMessageBox.Yes:
            self.dialog_network_import_openstreetmap = NetworkImportOpenstreetmap()
            self.dialog_network_import_openstreetmap.show()
        elif result == QMessageBox.No:
            iface = tessngIFace()
            win = iface.guiInterface().mainWindow()
            # 显示在线地图
            win.showOsmInline(True)

    # 1.4.导入Excel
    def network_import_excel(self):
        self.dialog_network_import_excel = NetworkImportExcel()
        self.dialog_network_import_excel.show()

    # 2.1.导出为OpenDrive
    def network_export_opendrive(self):
        self.dialog_network_export_opendrive = NetworkExportOpendrive()
        self.dialog_network_export_opendrive.show()

    # 2.2.导出为Shape
    def network_export_shape(self):
        self.dialog_network_export_shape = NetworkExportShape()
        self.dialog_network_export_shape.show()

    # 2.3.导出为GeoJson
    def network_export_geojson(self):
        self.dialog_network_export_geojson = NetworkExportGeojson()
        self.dialog_network_export_geojson.show()

    # 2.4.导出为Unity
    def network_export_unity(self):
        self.dialog_network_export_unity = NetworkExportUnity()

    # 2.5.导出为Json
    def network_export_json(self):
        self.dialog_network_export_json = NetworkExportJson()
        self.dialog_network_export_json.show()

    # 3.1.创建路段
    def network_edit_create(self):
        iface = tessngIFace()
        guiiface = iface.guiInterface()
        # 将按钮修改成【取消工具】
        guiiface.actionNullGMapTool().trigger()
        #
        self.dialog_network_edit_create = NetworkEditCreate()
        self.dialog_network_edit_create.show()

    # 3.2.打断路段
    def network_edit_split(self):
        iface = tessngIFace()
        guiiface = iface.guiInterface()
        # 获取按钮状态
        action = self.action_network_edit_split
        if action.isChecked():
            GlobalVar.is_need_split_link = True
            action.setText("取消选中打断路段")
            # 将按钮修改成【取消工具】
            guiiface.actionNullGMapTool().trigger()

            # 关联函数
            def disconnect(menu):
                menu.action_network_edit_split.setChecked(False)
                menu.action_network_edit_split.setText("打断路段")
                GlobalVar.is_need_split_link = False
            # 把其他关联上
            for actions in [guiiface.netToolBar().actions(), guiiface.operToolBar().actions()]:
                for action in actions:
                    if action.text() == "取消工具":
                        continue
                    action.triggered.connect(partial(disconnect, self))

            Tools.show_info_box("请右击需要打断的位置来打断路段！")
        else:
            GlobalVar.is_need_split_link = False
            action.setText("打断路段")

    # 3.3.合并路段
    def network_edit_connect(self):
        iface = tessngIFace()
        netiface = iface.netInterface()
        # 1.执行连接
        state, message = link_edit.joinLink(netiface)
        # 2.显示信息
        if state:
            Tools.show_info_box("路段合并完成")
            Logger.logger_network.info("The connection of links has been finished:\n"+message)
        else:
            Tools.show_info_box(message, "warning")

    # 3.4.简化路网
    def network_edit_simplify(self):
        self.dialog_network_edit_simplify = NetworkEditSimplify()
        self.dialog_network_edit_simplify.show()

    # 4.导出轨迹
    def trajectory_export(self):
        self.dialog_trajectory_export = TrajectoryExport()
        self.dialog_trajectory_export.show()

    # 5.1.打开说明书
    def open_instruction(self):
        open_file(Tools.instruction_path, new=2)

    # 5.2.打开样例
    def open_examples(self):
        open_folder(['explorer', Tools.examples_path], shell=True)

    # 5.3.提出建议
    def send_advise(self):
        self.dialog_send_advise = SendAdvise()
        self.dialog_send_advise.show()


# 1.1.导入OpenDrive
class NetworkImportOpendrive(QWidget):
    # 用类变量记住之前的选择
    file_path = None

    def __init__(self):
        super().__init__()
        self.name = "导入OpenDrive"
        self.width = 300
        self.height = 200
        self.format = [("OpenDrive", "xodr")]
        self.mode = "opendrive"

        # 设置界面属性
        Tools.set_attribution(self)
        # 设置界面布局
        self.set_layout()

    # 设置界面布局
    def set_layout(self):
        # 第一行：文本框和按钮
        self.lineEdit = QLineEdit()
        self.lineEdit.setFixedWidth(500)
        self.button_select_file = QPushButton('文件选择')
        horizontal_layout_1 = QHBoxLayout()
        horizontal_layout_1.addWidget(self.lineEdit)
        horizontal_layout_1.addWidget(self.button_select_file)
        # 第二行：文本和下拉框
        self.label_select_length = QLabel("路段最小分段长度：")
        self.combo = QComboBox()
        self.combo.addItems(("1 m", "3 m", "5 m", "10 m", "20 m"))
        horizontal_layout_2 = QHBoxLayout()
        horizontal_layout_2.addWidget(self.label_select_length)
        horizontal_layout_2.addWidget(self.combo)
        # 第三行：文本框
        self.label_select_type = QLabel("生成车道类型：")
        # 第四行：多选栏
        self.checkBox_1 = QCheckBox('机动车道')
        self.checkBox_2 = QCheckBox('非机动车道')
        self.checkBox_3 = QCheckBox('人行道')
        self.checkBox_4 = QCheckBox('应急车道')
        self.checkBoxes = [self.checkBox_1, self.checkBox_2, self.checkBox_3, self.checkBox_4]
        horizontal_layout_3 = QHBoxLayout()
        for checkBox in self.checkBoxes:
            horizontal_layout_3.addWidget(checkBox)
        # 第五行：按钮
        self.button = QPushButton('生成路网文件')

        # 总体布局
        layout = QVBoxLayout()
        layout.addLayout(horizontal_layout_1)
        layout.addLayout(horizontal_layout_2)
        layout.addWidget(self.label_select_type)
        layout.addLayout(horizontal_layout_3)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 设置关联关系
        # 监测组件变动
        self.lineEdit.textChanged.connect(self.monitor_state)
        for checkBox in self.checkBoxes:
            checkBox.stateChanged.connect(self.monitor_state)
        # 关联按钮与调用函数
        self.button_select_file.clicked.connect(self.select_file)
        self.button.clicked.connect(self.create_network)

        # 设置默认模式和初始状态
        if NetworkImportOpendrive.file_path:
            self.lineEdit.setText(NetworkImportOpendrive.file_path)
        self.combo.setCurrentIndex(0)
        for checkBox in self.checkBoxes:
            checkBox.setCheckState(Qt.Checked)
        self.monitor_state()

    # 监测各组件状态，切换控件的可用状态
    def monitor_state(self):
        # 获取状态
        file_path = self.lineEdit.text()
        isfile = os.path.isfile(file_path)
        checkbox_isChecked = any(checkbox.isChecked() for checkbox in self.checkBoxes)
        enabled = isfile and checkbox_isChecked

        # 设置可用状态
        self.button.setEnabled(enabled)

    # 选择文件
    def select_file(self):
        file_path = Tools.open_file(self.format)
        if file_path:
            # 显示文件路径在LineEdit中
            self.lineEdit.setText(file_path)

            NetworkImportOpendrive.file_path = file_path

    # 创建路网
    def create_network(self):
        # 获取文件名
        file_path = self.lineEdit.text()
        # 获取分段长度
        step_length = float(self.combo.currentText().split()[0])
        # 获取车道类型
        lane_types = [checkbox.text() for checkbox in self.checkBoxes if checkbox.isChecked()]
        # 构建参数
        params = {
            "file_path": file_path,
            "step_length": step_length,
            "lane_types": lane_types,
        }
        # 执行创建
        Tools.network_import(self, params)


# 1.2.导入Shape
class NetworkImportShape(QWidget):
    def __init__(self):
        super().__init__()
        self.name = "导入Shape"
        self.width = 300
        self.height = 200
        self.format = None
        self.mode = "shape"

        # 标签信息
        self.info_need_file = "待选择文件"
        self.info_no_file = "该路径下无合法文件"
        self.info_not_need_file = "不选择文件"
        self.proj_modes = ("prj文件投影", "高斯克吕格投影(tmerc)", "通用横轴墨卡托投影(utm)", "Web墨卡托投影(web)",)

        # 设置界面属性
        Tools.set_attribution(self)
        # 设置界面布局
        self.set_layout()

    # 设置界面布局
    def set_layout(self):
        # 第一行：文本框和按钮
        self.lineEdit = QLineEdit()
        self.lineEdit.setFixedWidth(500)
        self.button_select_folder = QPushButton('文件夹选择')
        horizontal_layout_1 = QHBoxLayout()
        horizontal_layout_1.addWidget(self.lineEdit)
        horizontal_layout_1.addWidget(self.button_select_folder)
        # 第二行：单选框
        self.label_select_coordType = QLabel("读取坐标类型：")
        self.radio_coordType_dke = QRadioButton('笛卡尔坐标')
        self.radio_coordType_jwd = QRadioButton('经纬度坐标')
        self.radio_group_coordType = QButtonGroup(self)
        self.radio_group_coordType.addButton(self.radio_coordType_dke)
        self.radio_group_coordType.addButton(self.radio_coordType_jwd)
        horizontal_layout_2 = QHBoxLayout()
        horizontal_layout_2.addWidget(self.label_select_coordType)
        horizontal_layout_2.addWidget(self.radio_coordType_dke)
        horizontal_layout_2.addWidget(self.radio_coordType_jwd)
        # 第三行：单选框
        self.label_select_laneDataType = QLabel("导入车道数据类型：")
        self.radio_laneDataType_center = QRadioButton('车道中心线')
        self.radio_laneDataType_boundary = QRadioButton('车道边界线')
        self.radio_group_laneDataType = QButtonGroup(self)
        self.radio_group_laneDataType.addButton(self.radio_laneDataType_center)
        self.radio_group_laneDataType.addButton(self.radio_laneDataType_boundary)
        horizontal_layout_3 = QHBoxLayout()
        horizontal_layout_3.addWidget(self.label_select_laneDataType)
        horizontal_layout_3.addWidget(self.radio_laneDataType_center)
        horizontal_layout_3.addWidget(self.radio_laneDataType_boundary)
        # 第四行：下拉框
        self.label_selcet_laneFileName = QLabel("路段车道文件名称：")
        self.combo_laneFileName = QComboBox()
        self.combo_laneFileName.addItems((self.info_need_file,))
        horizontal_layout_4 = QHBoxLayout()
        horizontal_layout_4.addWidget(self.label_selcet_laneFileName)
        horizontal_layout_4.addWidget(self.combo_laneFileName)
        # 第五行：下拉框
        self.label_select_laneConnFileName = QLabel("连接段车道文件名称：")
        self.combo_laneConnFileName = QComboBox()
        self.combo_laneConnFileName.addItems((self.info_need_file,))
        horizontal_layout_5 = QHBoxLayout()
        horizontal_layout_5.addWidget(self.label_select_laneConnFileName)
        horizontal_layout_5.addWidget(self.combo_laneConnFileName)
        # 第六行：下拉框
        self.label_select_proj = QLabel("投影方式：")
        self.combo_proj = QComboBox()
        self.combo_proj.addItems(self.proj_modes)
        horizontal_layout_6 = QHBoxLayout()
        horizontal_layout_6.addWidget(self.label_select_proj)
        horizontal_layout_6.addWidget(self.combo_proj)
        # 第七行：按钮
        self.button = QPushButton('生成路网文件')

        # 总体布局
        layout = QVBoxLayout()
        layout.addLayout(horizontal_layout_1)
        layout.addLayout(horizontal_layout_2)
        layout.addLayout(horizontal_layout_3)
        layout.addLayout(horizontal_layout_4)
        layout.addLayout(horizontal_layout_5)
        layout.addLayout(horizontal_layout_6)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 设置关联关系
        # 监测组件变动
        self.lineEdit.textChanged.connect(self.monitor_state)
        self.radio_coordType_dke.toggled.connect(self.monitor_state_radio_coordType)
        # 关联按钮与调用函数
        self.button_select_folder.clicked.connect(self.select_folder)
        self.button.clicked.connect(self.create_network)

        # 设置默认模式与初始状态
        self.radio_coordType_dke.setChecked(True)
        self.radio_laneDataType_center.setChecked(True)
        self.monitor_state()

    # 监测各组件状态，切换控件的可用状态
    def monitor_state(self):
        # 获取文件夹路径
        folder_path = self.lineEdit.text()
        # 判断文件夹是否存在
        isdir = os.path.isdir(folder_path)
        # 设置下拉框状态
        self.set_combo(folder_path, isdir)
        # 获取下拉框状态
        combo = all(
            combo_text not in [self.info_need_file, self.info_no_file]
            for combo_text in [self.combo_laneFileName.currentText(), self.combo_laneConnFileName.currentText()]
        )
        enabled = isdir and combo

        # 设置可用状态
        self.button.setEnabled(enabled)

    def monitor_state_radio_coordType(self):
        # 笛卡尔还是经纬度
        is_use_lon_and_lat = self.radio_coordType_jwd.isChecked()
        # 下拉框状态
        self.combo_proj.setEnabled(is_use_lon_and_lat)

    # 设置下拉框状态
    def set_combo(self, folder_path, isdir):
        # 车道文件和车道连接文件
        if not folder_path:
            new_items_laneFileName = new_items_laneConnFileName = (self.info_need_file,)
        elif isdir:
            public_file = self.read_public_files(folder_path)
            if public_file:
                new_items_laneFileName = tuple(public_file)
                new_items_laneConnFileName = (self.info_not_need_file,) + tuple(public_file)
            else:
                new_items_laneFileName = new_items_laneConnFileName = (self.info_no_file,)
        else:
            new_items_laneFileName = new_items_laneConnFileName = (self.info_no_file,)
        # 重新设置QComboBox
        self.combo_laneFileName.clear()
        self.combo_laneConnFileName.clear()
        self.combo_laneFileName.addItems(new_items_laneFileName)
        self.combo_laneConnFileName.addItems(new_items_laneConnFileName)
        # self.combo_laneFileName.setCurrentIndex(0)
        # self.combo_laneConnFileName.setCurrentIndex(0)

        # 投影文件
        is_have_prj_file = False
        if folder_path and isdir:
            laneFileName = self.combo_laneFileName.currentText()
            filePath_prj = os.path.join(folder_path, f"{laneFileName}.prj")
            if os.path.exists(filePath_prj):
                # 读取投影文件
                proj_string_file = open(filePath_prj, "r").read()
                if "PROJCS" in proj_string_file:
                    # proj_string = proj_string_file
                    is_have_prj_file = True
        if not is_have_prj_file:
            self.combo_proj.setItemText(0, "（无自带投影）")
            if self.combo_proj.currentIndex() == 0:
                self.combo_proj.setCurrentIndex(1)
            self.combo_proj.model().item(0).setEnabled(False)
        else:
            self.combo_proj.setItemText(0, self.proj_modes[0])
            self.combo_proj.setCurrentIndex(0)
            self.combo_proj.model().item(0).setEnabled(True)

    # 读取文件夹里的公共文件
    def read_public_files(self, folder_path):
        items = os.listdir(folder_path)
        # file_dict = {".cpg": [], ".dbf": [], ".shp": [], ".shx": []}
        file_dict = {".dbf": [], ".shp": []}
        # 遍历每个文件和文件夹
        for item in items:
            item_path = os.path.join(folder_path, item)
            # 如果是文件
            if os.path.isfile(item_path):
                file_name, extension = os.path.splitext(item)
                if extension in file_dict:
                    file_dict[extension].append(file_name)
        public_file = reduce(set.intersection, map(set, file_dict.values())) or None
        return sorted(public_file)

    # 选择文件夹
    def select_folder(self):
        folder_path = Tools.open_folder()
        if folder_path:
            # 显示文件路径在LineEdit中
            self.lineEdit.setText(folder_path)

    # 创建路网
    def create_network(self):
        # 获取路径
        folder_path = self.lineEdit.text()
        # 获取坐标类型
        is_use_lon_and_lat = self.radio_coordType_jwd.isChecked()
        # 获取车道数据类型
        is_use_center_line = self.radio_laneDataType_center.isChecked()
        # 获取车道文件名称
        laneFileName = self.combo_laneFileName.currentText()
        # 获取车道连接文件名称
        laneConnectorFileName = self.combo_laneConnFileName.currentText()
        # 获取投影方式
        proj_mode = self.combo_proj.currentText()
        # 构建参数
        params = {
            "folder_path": folder_path,
            "is_use_lon_and_lat": is_use_lon_and_lat,
            "is_use_center_line": is_use_center_line,
            "laneFileName": laneFileName,
            "laneConnectorFileName": laneConnectorFileName,
            "proj_mode": proj_mode,
        }
        # 核查shape文件
        is_ok = self.check_shapefile(folder_path, laneFileName, is_use_lon_and_lat)
        # 执行创建
        if is_ok:
            Tools.network_import(self, params)

    def check_shapefile(self, folder_path, laneFileName, is_use_lon_and_lat):
        try:
            from ..Toolbox.other2tess.shape2tess.shape2tess import check_shapefile
            is_ok, prompt_information = check_shapefile(folder_path, laneFileName, is_use_lon_and_lat)
            if not is_ok:
                Tools.show_info_box(prompt_information, "warning")
            return is_ok
        except:
            Logger.logger_network.warning("没有核验shape文件的坐标类型")
            return True


# 1.3.导入OpenStreetMap
class NetworkImportOpenstreetmap(QWidget):
    def __init__(self):
        super().__init__()
        self.name = "导入OpenStreetMap"
        self.width = 300
        self.height = 200
        self.format = [("OpenStreetMap", "osm")]
        self.mode = "osm"

        # 设置界面属性
        Tools.set_attribution(self)
        # 设置界面布局
        self.set_layout()

    # 设置界面布局
    def set_layout(self):
        # 第一行：文本框和按钮
        self.lineEdit_offline_select_file = QLineEdit()
        self.lineEdit_offline_select_file.setFixedWidth(500)
        self.button_offline_select_file = QPushButton('文件选择')
        horizontal_layout_offline_1 = QHBoxLayout()
        horizontal_layout_offline_1.addWidget(self.lineEdit_offline_select_file)
        horizontal_layout_offline_1.addWidget(self.button_offline_select_file)
        # 第二行：勾选框
        self.label_select_roadType = QLabel("导入道路类型：")
        self.checkBox_1 = QCheckBox('高速公路')
        self.checkBox_2 = QCheckBox('主干道路')
        self.checkBox_3 = QCheckBox('低等级道路')
        self.checkBoxes = [self.checkBox_1, self.checkBox_2, self.checkBox_3]
        horizontal_layout_offline_2 = QHBoxLayout()
        horizontal_layout_offline_2.addWidget(self.label_select_roadType)
        for checkBox in self.checkBoxes:
            horizontal_layout_offline_2.addWidget(checkBox)
        # 第三行：按钮
        self.button = QPushButton('生成路网文件')

        # 总体布局
        layout = QVBoxLayout()
        layout.addLayout(horizontal_layout_offline_1)
        layout.addLayout(horizontal_layout_offline_2)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 设置关联关系
        # 监测组件变动
        self.lineEdit_offline_select_file.textChanged.connect(self.monitor_state)
        self.checkBox_2.stateChanged.connect(self.monitor_state_checkBox_2)
        self.checkBox_3.stateChanged.connect(self.monitor_state_checkBox_3)
        # 关联按钮与调用函数
        self.button_offline_select_file.clicked.connect(self.select_file)
        self.button.clicked.connect(self.create_network)

        # 设置默认模式和初始状态
        # 设置默认勾选状态
        self.checkBox_1.setChecked(True)
        self.checkBox_2.setChecked(True)
        self.checkBox_3.setChecked(True)
        # 使复选框不可改动
        self.checkBox_1.setEnabled(False)
        self.monitor_state()

    # 监测各组件状态，切换控件的可用状态
    def monitor_state(self):
        # 按钮状态
        file_path = self.lineEdit_offline_select_file.text()
        isfile = os.path.isfile(file_path)

        # 设置可用状态
        self.button.setEnabled(isfile)

    def monitor_state_checkBox_2(self):
        if not self.checkBox_2.isChecked() and self.checkBox_3.isChecked():
            self.checkBox_3.setChecked(False)

    def monitor_state_checkBox_3(self):
        if not self.checkBox_2.isChecked() and self.checkBox_3.isChecked():
            self.checkBox_2.setChecked(True)

    # 选择文件
    def select_file(self):
        file_path = Tools.open_file(self.format)
        if file_path:
            # 显示文件路径在LineEdit中
            self.lineEdit_offline_select_file.setText(file_path)

    # 创建路网
    def create_network(self):
        # 导入文件
        file_path = self.lineEdit_offline_select_file.text()
        # 确定导入道路等级
        if not self.checkBox_2.isChecked():
            road_class = 1
        elif self.checkBox_2.isChecked() and not self.checkBox_3.isChecked():
            road_class = 2
        else:
            road_class = 3
        # 构建参数
        params = {
            "osm_file_path": file_path,
            "road_class": road_class,
            "save_data_path": Tools.osm_path,
        }
        # 执行创建
        Tools.network_import(self, params)

    # 创建路网
    @staticmethod
    def create_network_online(lon_1, lat_1, lon_2, lat_2, parseLevel):
        lon_min = min(lon_1, lon_2)
        lat_min = min(lat_1, lat_2)
        lon_max = max(lon_1, lon_2)
        lat_max = max(lat_1, lat_2)

        road_class = parseLevel
        # 构建参数
        bounding_box = {
            "lon_min": lon_min,
            "lon_max": lon_max,
            "lat_min": lat_min,
            "lat_max": lat_max,
        }
        params = {
            "bounding_box": bounding_box,
            "road_class": road_class,
            "save_data_path": Tools.osm_path,
        }
        # 构建空类
        class Widget: name, mode, close = "在线导入OSM", "osm", lambda self: None
        # 执行创建
        Tools.network_import(Widget(), params)


# 1.4.导入Excel
class NetworkImportExcel(QWidget):
    def __init__(self):
        super().__init__()
        self.name = "导入Excel"
        self.width = 300
        self.height = 200
        self.format = [("Excel", "xlsx"), ("Excel", "xls"), ("CSV", "csv")]
        self.mode = "excel"

        # 设置界面属性
        Tools.set_attribution(self)
        # 设置界面布局
        self.set_layout()

    # 设置界面布局
    def set_layout(self):
        # 第一行：文本框和按钮
        self.lineEdit = QLineEdit()
        self.lineEdit.setFixedWidth(500)
        self.button_select_file = QPushButton('文件选择')
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.lineEdit)
        horizontal_layout.addWidget(self.button_select_file)
        # 第二行：按钮
        self.button = QPushButton('生成路网文件')

        # 总体布局
        layout = QVBoxLayout()
        layout.addLayout(horizontal_layout)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 设置关联关系
        # 监测组件变动
        self.lineEdit.textChanged.connect(self.monitor_state)
        # 关联按钮与调用函数
        self.button_select_file.clicked.connect(self.select_file)
        self.button.clicked.connect(self.create_network)

        # 设置默认模式和初始状态
        self.monitor_state()

    # 监测各组件状态，切换控件的可用状态
    def monitor_state(self):
        file_path = self.lineEdit.text()
        enabled = os.path.isfile(file_path)

        # 设置可用状态
        self.button.setEnabled(enabled)

    # 选择文件
    def select_file(self):
        file_path = Tools.open_file(self.format)
        if file_path:
            # 显示文件路径在LineEdit中
            self.lineEdit.setText(file_path)

    # 创建路网
    def create_network(self):
        # 获取路径
        file_path = self.lineEdit.text()
        # 构建参数
        params = {
            "file_path": file_path,
        }
        # 执行创建
        Tools.network_import(self, params)


# 2.1.导出为OpenDrive
class NetworkExportOpendrive(QWidget):
    def __init__(self):
        super().__init__()
        self.name = "导出为OpenDrive"
        self.width = 400
        self.height = 200
        self.format = ("OpenDrive", "xodr")
        self.mode = "opendrive"

        # 设置界面属性
        Tools.set_attribution(self)
        # 设置界面布局
        self.set_layout()

    # 设置界面布局
    def set_layout(self):
        self.file_proj_string, file_proj_info = Tools.read_file_proj()

        # 第一行：勾选框
        self.checkBox = QCheckBox('将投影关系写入header')
        # 第二行：单选框
        self.radio_proj_file = QRadioButton('使用路网创建时的投影')
        # 第三行：文本
        self.lineEdit_proj_file = QLineEdit(file_proj_info)
        # 第四行：单选框
        self.radio_proj_custom = QRadioButton('使用自定义高斯克吕格投影')
        # 第五行：文本和输入框，使用水平布局
        self.label_proj_custom_lon = QLabel('投影中心经度：')
        self.lineEdit_proj_custom_lon = QLineEdit()
        horizontal_layout_lon = QHBoxLayout()
        horizontal_layout_lon.addWidget(self.label_proj_custom_lon)
        horizontal_layout_lon.addWidget(self.lineEdit_proj_custom_lon)
        # 第六行：文本和输入框，使用水平布局
        self.label_proj_custom_lat = QLabel('投影中心纬度：')
        self.lineEdit_proj_custom_lat = QLineEdit()
        horizontal_layout_lat = QHBoxLayout()
        horizontal_layout_lat.addWidget(self.label_proj_custom_lat)
        horizontal_layout_lat.addWidget(self.lineEdit_proj_custom_lat)
        # 第七行：按钮
        self.button = QPushButton('导出')

        # 限制输入框内容
        validator_coord = QDoubleValidator()
        self.lineEdit_proj_custom_lon.setValidator(validator_coord)
        self.lineEdit_proj_custom_lat.setValidator(validator_coord)

        # Box布局
        group_box = QGroupBox()
        group_box_layout = QVBoxLayout()
        group_box_layout.addWidget(self.radio_proj_file)
        group_box_layout.addWidget(self.lineEdit_proj_file)
        group_box_layout.addWidget(self.radio_proj_custom)
        group_box_layout.addLayout(horizontal_layout_lon)
        group_box_layout.addLayout(horizontal_layout_lat)
        group_box.setLayout(group_box_layout)

        # 总体布局
        layout = QVBoxLayout()
        layout.addWidget(self.checkBox)
        layout.addWidget(group_box)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 设置关联关系
        # 监测组件变动
        self.checkBox.stateChanged.connect(self.monitor_state)
        self.radio_proj_custom.toggled.connect(self.monitor_state)
        self.lineEdit_proj_custom_lon.textChanged.connect(self.monitor_state)
        self.lineEdit_proj_custom_lat.textChanged.connect(self.monitor_state)
        # 关联按钮与调用函数
        self.button.clicked.connect(partial(Tools.network_export, self))

        # 设置默认模式和初始状态
        if bool(self.file_proj_string):
            self.radio_proj_file.setChecked(True)
        else:
            self.radio_proj_custom.setChecked(True)
        self.monitor_state()

    # 监测各组件状态，切换控件的可用状态
    def monitor_state(self):
        # 勾选框的状态
        enabled_checkBox = self.checkBox.isChecked()
        # 文件投影的状态
        enabled_proj_file = bool(self.file_proj_string)
        # 选择投影方式的状态
        enabled_radio_proj = self.radio_proj_custom.isChecked()
        # 按钮状态
        enabled_button = True
        if enabled_checkBox and enabled_radio_proj:
            lon_0 = self.lineEdit_proj_custom_lon.text()
            lat_0 = self.lineEdit_proj_custom_lat.text()
            if not (lon_0 and lat_0 and -180 < float(lon_0) < 180 and -90 < float(lat_0) < 90):
                enabled_button = False

        # 设置可用状态
        self.radio_proj_file.setEnabled(enabled_checkBox and enabled_proj_file)
        self.lineEdit_proj_file.setEnabled(enabled_checkBox and enabled_proj_file and not enabled_radio_proj)
        self.radio_proj_custom.setEnabled(enabled_checkBox)
        self.label_proj_custom_lon.setEnabled(enabled_checkBox and enabled_radio_proj)
        self.label_proj_custom_lat.setEnabled(enabled_checkBox and enabled_radio_proj)
        self.lineEdit_proj_custom_lon.setEnabled(enabled_checkBox and enabled_radio_proj)
        self.lineEdit_proj_custom_lat.setEnabled(enabled_checkBox and enabled_radio_proj)
        self.button.setEnabled(enabled_button)


# 2.2.导出为Shape
class NetworkExportShape(QWidget):
    def __init__(self):
        super().__init__()
        self.name = "导出为Shape"
        self.width = 400
        self.height = 300
        self.format = ("Shape", "shp")
        self.mode = "shape"

        # 设置界面属性
        Tools.set_attribution(self)
        # 设置界面布局
        self.set_layout()

    # 设置界面布局
    def set_layout(self):
        self.file_proj_string, file_proj_info = Tools.read_file_proj()

        # 第一行：单选框
        self.radio_coord_1 = QRadioButton('笛卡尔坐标')
        # 第二行：单选框
        self.radio_coord_2 = QRadioButton('经纬度坐标')
        # 第三行：单选框
        self.radio_proj_file = QRadioButton('使用路网创建时的投影')
        # 第四行：文本
        self.lineEdit_proj_file = QLineEdit(file_proj_info)
        # 第五行：单选框
        self.radio_proj_custom = QRadioButton('使用自定义高斯克吕格投影')
        # 第六行：文本和输入框，使用水平布局
        self.label_proj_custom_lon = QLabel('投影中心经度：')
        self.lineEdit_proj_custom_lon = QLineEdit()
        horizontal_layout_lon = QHBoxLayout()
        horizontal_layout_lon.addWidget(self.label_proj_custom_lon)
        horizontal_layout_lon.addWidget(self.lineEdit_proj_custom_lon)
        # 第七行：文本和输入框，使用水平布局
        self.label_proj_custom_lat = QLabel('投影中心纬度：')
        self.lineEdit_proj_custom_lat = QLineEdit()
        horizontal_layout_lat = QHBoxLayout()
        horizontal_layout_lat.addWidget(self.label_proj_custom_lat)
        horizontal_layout_lat.addWidget(self.lineEdit_proj_custom_lat)
        # 第八行：按钮
        self.button = QPushButton('导出')

        # 限制输入框内容
        validator_coord = QDoubleValidator()
        self.lineEdit_proj_custom_lon.setValidator(validator_coord)
        self.lineEdit_proj_custom_lat.setValidator(validator_coord)

        # Box布局
        group_box = QGroupBox()
        group_box_layout = QVBoxLayout()
        group_box_layout.addWidget(self.radio_proj_file)
        group_box_layout.addWidget(self.lineEdit_proj_file)
        group_box_layout.addWidget(self.radio_proj_custom)
        group_box_layout.addLayout(horizontal_layout_lon)
        group_box_layout.addLayout(horizontal_layout_lat)
        group_box.setLayout(group_box_layout)

        # 总体布局
        layout = QVBoxLayout()
        layout.addWidget(self.radio_coord_1)
        layout.addWidget(self.radio_coord_2)
        layout.addWidget(group_box)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 设置关联关系
        # 监测组件变动
        self.radio_coord_1.toggled.connect(self.monitor_state)
        self.radio_proj_custom.toggled.connect(self.monitor_state)
        self.lineEdit_proj_custom_lon.textChanged.connect(self.monitor_state)
        self.lineEdit_proj_custom_lat.textChanged.connect(self.monitor_state)
        # 关联按钮与调用函数
        self.button.clicked.connect(partial(Tools.network_export, self))

        # 设置默认模式和初始状态
        self.radio_coord_1.setChecked(True)
        if bool(self.file_proj_string):
            self.radio_proj_file.setChecked(True)
        else:
            self.radio_proj_custom.setChecked(True)
        self.monitor_state()

    # 监测各组件状态，切换控件的可用状态
    def monitor_state(self):
        # 勾选框的状态
        enabled_coord = self.radio_coord_2.isChecked()
        # 文件投影的状态
        enabled_proj_file = bool(self.file_proj_string)
        # 选择投影方式的状态
        enabled_radio_proj = self.radio_proj_custom.isChecked()
        # 按钮状态
        enabled_button = True
        if enabled_coord and enabled_radio_proj:
            lon_0 = self.lineEdit_proj_custom_lon.text()
            lat_0 = self.lineEdit_proj_custom_lat.text()
            if not (lon_0 and lat_0 and -180 < float(lon_0) < 180 and -90 < float(lat_0) < 90):
                enabled_button = False

        # 设置可用状态
        self.radio_coord_1.setChecked(not enabled_coord)
        self.radio_coord_2.toggled.connect(self.monitor_state)
        self.radio_proj_file.setEnabled(enabled_coord and enabled_proj_file)
        self.lineEdit_proj_file.setEnabled(enabled_coord and enabled_proj_file and not enabled_radio_proj)
        self.radio_proj_custom.setEnabled(enabled_coord)
        self.label_proj_custom_lon.setEnabled(enabled_coord and enabled_radio_proj)
        self.label_proj_custom_lat.setEnabled(enabled_coord and enabled_radio_proj)
        self.lineEdit_proj_custom_lon.setEnabled(enabled_coord and enabled_radio_proj)
        self.lineEdit_proj_custom_lat.setEnabled(enabled_coord and enabled_radio_proj)
        self.button.setEnabled(enabled_button)


# 2.3.导出为GeoJson
class NetworkExportGeojson(QWidget):
    def __init__(self):
        super().__init__()
        self.name = "导出为GeoJson"
        self.width = 400
        self.height = 300
        self.format = ("GeoJson", "geojson")
        self.mode = "geojson"

        # 设置界面属性
        Tools.set_attribution(self)
        # 设置界面布局
        self.set_layout()

    # 设置界面布局
    def set_layout(self):
        self.file_proj_string, file_proj_info = Tools.read_file_proj()

        # 第一行：单选框
        self.radio_coord_1 = QRadioButton('笛卡尔坐标')
        # 第二行：单选框
        self.radio_coord_2 = QRadioButton('经纬度坐标')
        # 第三行：单选框
        self.radio_proj_file = QRadioButton('使用路网创建时的投影')
        # 第四行：文本
        self.lineEdit_proj_file = QLineEdit(file_proj_info)
        # 第五行：单选框
        self.radio_proj_custom = QRadioButton('使用自定义高斯克吕格投影')
        # 第六行：文本和输入框，使用水平布局
        self.label_proj_custom_lon = QLabel('投影中心经度：')
        self.lineEdit_proj_custom_lon = QLineEdit()
        horizontal_layout_lon = QHBoxLayout()
        horizontal_layout_lon.addWidget(self.label_proj_custom_lon)
        horizontal_layout_lon.addWidget(self.lineEdit_proj_custom_lon)
        # 第七行：文本和输入框，使用水平布局
        self.label_proj_custom_lat = QLabel('投影中心纬度：')
        self.lineEdit_proj_custom_lat = QLineEdit()
        horizontal_layout_lat = QHBoxLayout()
        horizontal_layout_lat.addWidget(self.label_proj_custom_lat)
        horizontal_layout_lat.addWidget(self.lineEdit_proj_custom_lat)
        # 第八行：按钮
        self.button = QPushButton('导出')

        # 限制输入框内容
        validator_coord = QDoubleValidator()
        self.lineEdit_proj_custom_lon.setValidator(validator_coord)
        self.lineEdit_proj_custom_lat.setValidator(validator_coord)

        # Box布局
        group_box = QGroupBox()
        group_box_layout = QVBoxLayout()
        group_box_layout.addWidget(self.radio_proj_file)
        group_box_layout.addWidget(self.lineEdit_proj_file)
        group_box_layout.addWidget(self.radio_proj_custom)
        group_box_layout.addLayout(horizontal_layout_lon)
        group_box_layout.addLayout(horizontal_layout_lat)
        group_box.setLayout(group_box_layout)

        # 总体布局
        layout = QVBoxLayout()
        layout.addWidget(self.radio_coord_1)
        layout.addWidget(self.radio_coord_2)
        layout.addWidget(group_box)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 设置关联关系
        # 监测组件变动
        self.radio_coord_1.toggled.connect(self.monitor_state)
        self.radio_coord_2.toggled.connect(self.monitor_state)
        self.radio_proj_custom.toggled.connect(self.monitor_state)
        self.lineEdit_proj_custom_lon.textChanged.connect(self.monitor_state)
        self.lineEdit_proj_custom_lat.textChanged.connect(self.monitor_state)
        # 关联按钮与调用函数
        self.button.clicked.connect(partial(Tools.network_export, self))

        # 设置默认模式和初始状态
        self.radio_coord_1.setChecked(True)
        if bool(self.file_proj_string):
            self.radio_proj_file.setChecked(True)
        else:
            self.radio_proj_custom.setChecked(True)
        self.monitor_state()

    # 监测各组件状态，切换控件的可用状态
    def monitor_state(self):
        # 勾选框的状态
        enabled_coord = self.radio_coord_2.isChecked()
        # 文件投影的状态
        enabled_proj_file = bool(self.file_proj_string)
        # 选择投影方式的状态
        enabled_radio_proj = self.radio_proj_custom.isChecked()
        # 按钮状态
        enabled_button = True
        if enabled_coord and enabled_radio_proj:
            lon_0 = self.lineEdit_proj_custom_lon.text()
            lat_0 = self.lineEdit_proj_custom_lat.text()
            if not (lon_0 and lat_0 and -180 < float(lon_0) < 180 and -90 < float(lat_0) < 90):
                enabled_button = False

        # 设置可用状态
        self.radio_coord_1.setChecked(not enabled_coord)
        self.radio_proj_file.setEnabled(enabled_coord and enabled_proj_file)
        self.lineEdit_proj_file.setEnabled(enabled_coord and enabled_proj_file and not enabled_radio_proj)
        self.radio_proj_custom.setEnabled(enabled_coord)
        self.label_proj_custom_lon.setEnabled(enabled_coord and enabled_radio_proj)
        self.label_proj_custom_lat.setEnabled(enabled_coord and enabled_radio_proj)
        self.lineEdit_proj_custom_lon.setEnabled(enabled_coord and enabled_radio_proj)
        self.lineEdit_proj_custom_lat.setEnabled(enabled_coord and enabled_radio_proj)
        self.button.setEnabled(enabled_button)


# 2.4.导出为Unity
class NetworkExportUnity():
    def __init__(self):
        self.name = "导出为Unity"
        self.format = ("Unity", "json")
        self.mode = "unity"

        self.file_proj_string = {}
        Tools.network_export(self)

    def close(self):
        pass


# 2.5.导出为Json
class NetworkExportJson(QWidget):
    def __init__(self):
        super().__init__()
        self.name = "导出为Json"
        self.width = 400
        self.height = 200
        self.format = ("Json", "json")
        self.mode = "json"

        # 设置界面属性
        Tools.set_attribution(self)
        # 设置界面布局
        self.set_layout()

    # 设置界面布局
    def set_layout(self):
        self.file_proj_string, file_proj_info = Tools.read_file_proj()

        # 第一行：勾选框
        self.checkBox = QCheckBox('写入经纬度坐标')
        # 第二行：单选框
        self.radio_proj_file = QRadioButton('使用路网创建时的投影')
        # 第三行：文本
        self.lineEdit_proj_file = QLineEdit(file_proj_info)
        # 第四行：单选框
        self.radio_proj_custom = QRadioButton('使用自定义高斯克吕格投影')
        # 第五行：文本和输入框，使用水平布局
        self.label_proj_custom_lon = QLabel('投影中心经度：')
        self.lineEdit_proj_custom_lon = QLineEdit()
        horizontal_layout_lon = QHBoxLayout()
        horizontal_layout_lon.addWidget(self.label_proj_custom_lon)
        horizontal_layout_lon.addWidget(self.lineEdit_proj_custom_lon)
        # 第六行：文本和输入框，使用水平布局
        self.label_proj_custom_lat = QLabel('投影中心纬度：')
        self.lineEdit_proj_custom_lat = QLineEdit()
        horizontal_layout_lat = QHBoxLayout()
        horizontal_layout_lat.addWidget(self.label_proj_custom_lat)
        horizontal_layout_lat.addWidget(self.lineEdit_proj_custom_lat)
        # 第七行：按钮
        self.button = QPushButton('导出')

        # 限制输入框内容
        validator_coord = QDoubleValidator()
        self.lineEdit_proj_custom_lon.setValidator(validator_coord)
        self.lineEdit_proj_custom_lat.setValidator(validator_coord)

        # Box布局
        group_box = QGroupBox()
        group_box_layout = QVBoxLayout()
        group_box_layout.addWidget(self.radio_proj_file)
        group_box_layout.addWidget(self.lineEdit_proj_file)
        group_box_layout.addWidget(self.radio_proj_custom)
        group_box_layout.addLayout(horizontal_layout_lon)
        group_box_layout.addLayout(horizontal_layout_lat)
        group_box.setLayout(group_box_layout)

        # 总体布局
        layout = QVBoxLayout()
        layout.addWidget(self.checkBox)
        layout.addWidget(group_box)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 设置关联关系
        # 监测组件变动
        self.checkBox.stateChanged.connect(self.monitor_state)
        self.radio_proj_custom.toggled.connect(self.monitor_state)
        self.lineEdit_proj_custom_lon.textChanged.connect(self.monitor_state)
        self.lineEdit_proj_custom_lat.textChanged.connect(self.monitor_state)
        # 关联按钮与调用函数
        self.button.clicked.connect(partial(Tools.network_export, self))

        # 设置默认模式和初始状态
        if bool(self.file_proj_string):
            self.radio_proj_file.setChecked(True)
        else:
            self.radio_proj_custom.setChecked(True)
        self.monitor_state()

    # 监测各组件状态，切换控件的可用状态
    def monitor_state(self):
        # 勾选框的状态
        enabled_checkBox = self.checkBox.isChecked()
        # 文件投影的状态
        enabled_proj_file = bool(self.file_proj_string)
        # 选择投影方式的状态
        enabled_radio_proj = self.radio_proj_custom.isChecked()
        # 按钮状态
        enabled_button = True
        if enabled_checkBox and enabled_radio_proj:
            lon_0 = self.lineEdit_proj_custom_lon.text()
            lat_0 = self.lineEdit_proj_custom_lat.text()
            if not (lon_0 and lat_0 and -180 < float(lon_0) < 180 and -90 < float(lat_0) < 90):
                enabled_button = False

        # 设置可用状态
        self.radio_proj_file.setEnabled(enabled_checkBox and enabled_proj_file)
        self.lineEdit_proj_file.setEnabled(enabled_checkBox and enabled_proj_file and not enabled_radio_proj)
        self.radio_proj_custom.setEnabled(enabled_checkBox)
        self.label_proj_custom_lon.setEnabled(enabled_checkBox and enabled_radio_proj)
        self.label_proj_custom_lat.setEnabled(enabled_checkBox and enabled_radio_proj)
        self.lineEdit_proj_custom_lon.setEnabled(enabled_checkBox and enabled_radio_proj)
        self.lineEdit_proj_custom_lat.setEnabled(enabled_checkBox and enabled_radio_proj)
        self.button.setEnabled(enabled_button)


# 3.1.创建路段
class NetworkEditCreate(QWidget):
    def __init__(self):
        super().__init__()
        self.name = "通过坐标创建路段"
        self.width = 300
        self.height = 150

        # 设置界面属性
        Tools.set_attribution(self)
        self.setGeometry(80, 200, self.width, self.height)
        # 设置界面布局
        self.set_layout()

    # 设置界面布局
    def set_layout(self):
        # 第一行：文本、下拉框、文本、输入框
        self.label_laneCount = QLabel('车道数：')
        self.combo_laneCount = QComboBox()
        self.combo_laneCount.addItems(("1", "2", "3", "4", "5", "6", "7", "8"))
        self.combo_laneCount.setFixedWidth(100)
        self.label_laneWidth = QLabel('    车道宽度：')
        self.lineEdit_laneWidth = QLineEdit()
        self.lineEdit_laneWidth.setFixedWidth(100)
        self.label_laneWidth_meter = QLabel('m')
        horizontal_layout_1 = QHBoxLayout()
        horizontal_layout_1.addWidget(self.label_laneCount)
        horizontal_layout_1.addWidget(self.combo_laneCount)
        horizontal_layout_1.addWidget(self.label_laneWidth)
        horizontal_layout_1.addWidget(self.lineEdit_laneWidth)
        horizontal_layout_1.addWidget(self.label_laneWidth_meter)
        # 第二行：文本、输入框
        self.label_lanePoints = QLabel('路段中心线坐标：')
        self.lineEdit_lanePoints = QLineEdit()
        # self.lineEdit_lanePoints.setFixedWidth(100)
        horizontal_layout_2 = QHBoxLayout()
        horizontal_layout_2.addWidget(self.label_lanePoints)
        horizontal_layout_2.addWidget(self.lineEdit_lanePoints)
        # 第三行：按钮
        self.button = QPushButton('创建路段')

        # 限制输入框内容
        regex = QRegExp("^([0-9](\.[0-9]{0,2})?|10(\.0+)?)$")  # 限制为0~10的浮点数，两位小数
        validator = QRegExpValidator(regex)
        self.lineEdit_laneWidth.setValidator(validator)

        # 设置提示信息
        self.lineEdit_lanePoints.setToolTip('x1 , y1 (, z1) ; …… ; xn , yn (, zn)')

        # 总体布局
        layout = QVBoxLayout()
        layout.addLayout(horizontal_layout_1)
        layout.addLayout(horizontal_layout_2)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 设置关联关系
        # 监测组件变动
        self.lineEdit_laneWidth.textChanged.connect(self.monitor_state)
        self.lineEdit_lanePoints.textChanged.connect(self.monitor_state)
        # 关联按钮与调用函数
        self.button.clicked.connect(self.create_link)

        # 设置默认模式和初始状态
        self.combo_laneCount.setCurrentIndex(2)
        self.lineEdit_laneWidth.setText("3.5")
        self.monitor_state()

    # 监测各组件状态，切换控件的可用状态
    def monitor_state(self):
        laneWidth = self.lineEdit_laneWidth.text()
        laneWidth = bool(laneWidth) and float(laneWidth)>0
        # 按钮状态
        enabled_button = False
        try:
            lane_points = self.lineEdit_lanePoints.text()
            lane_points = lane_points.replace("，", ",").replace("；", ";").replace(" ", "")
            lane_points = lane_points.split(";")
            num = set([len([float(value) for value in point.split(",")]) for point in lane_points])
            if len(lane_points) >= 2 and (num == {2} or num == {3}) and laneWidth:
                enabled_button = True
        except:
            pass

        # 设置可用状态
        self.button.setEnabled(enabled_button)

    # 创建路段
    def create_link(self):
        iface = tessngIFace()
        netiface = iface.netInterface()

        laneCount = int(self.combo_laneCount.currentText())
        laneWidth = float(self.lineEdit_laneWidth.text())
        lanePoints = self.lineEdit_lanePoints.text().replace("，", ",").replace("；", ";").replace(" ", "")

        link_edit.createLink(netiface, laneCount, laneWidth, lanePoints)


# 3.4.简化路网
class NetworkEditSimplify(QWidget):
    def __init__(self):
        super().__init__()
        self.name = "简化路网"
        self.width = 300
        self.height = 150

        # 设置界面属性
        Tools.set_attribution(self)
        # self.setGeometry(80, 200, self.width, self.height)
        # 设置界面布局
        self.set_layout()

    # 设置界面布局
    def set_layout(self):
        # 第一行：文本、输入框
        self.label_angle = QLabel('最大简化角度（°）：')
        self.lineEdit_angle = QLineEdit()
        self.lineEdit_angle.setFixedWidth(100)
        horizontal_layout_1 = QHBoxLayout()
        horizontal_layout_1.addWidget(self.label_angle)
        horizontal_layout_1.addWidget(self.lineEdit_angle)
        # 第二行：文本、输入框
        self.label_length = QLabel('最大简化距离（m）：')
        self.lineEdit_length = QLineEdit()
        self.lineEdit_length.setFixedWidth(100)
        horizontal_layout_2 = QHBoxLayout()
        horizontal_layout_2.addWidget(self.label_length)
        horizontal_layout_2.addWidget(self.lineEdit_length)
        # 第三行：按钮
        self.button = QPushButton('简化路网')

        # 总体布局
        layout = QVBoxLayout()
        layout.addLayout(horizontal_layout_1)
        layout.addLayout(horizontal_layout_2)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 限制输入框内容
        validator = QDoubleValidator()
        self.lineEdit_angle.setValidator(validator)
        self.lineEdit_length.setValidator(validator)

        # 设置提示信息
        self.lineEdit_angle.setToolTip('1<=angle<=5')
        self.lineEdit_length.setToolTip('1<=length<=200')

        # 设置关联关系
        # 监测组件变动
        self.lineEdit_angle.textChanged.connect(self.monitor_state)
        self.lineEdit_length.textChanged.connect(self.monitor_state)
        # 关联按钮与调用函数
        self.button.clicked.connect(self.simplify_network)

        # 设置默认模式和初始状态
        self.lineEdit_angle.setText("1")
        self.lineEdit_length.setText("50")
        self.monitor_state()

    # 监测各组件状态，切换控件的可用状态
    def monitor_state(self):
        angle = self.lineEdit_angle.text()
        length = self.lineEdit_length.text()
        # 按钮状态
        enabled_button = bool(angle) and bool(length) and "," not in angle and "," not in length and (1<=float(angle)<=5) and (1<=float(length)<=200)

        # 设置可用状态
        self.button.setEnabled(enabled_button)

    # 简化路网
    def simplify_network(self):
        iface = tessngIFace()
        netiface = iface.netInterface()

        # 1.判断有无路段
        if not netiface.linkCount():
            Tools.show_info_box("当前路网没有路段", "warning")
            return

        # 2.关闭窗口
        self.close()

        # 3.保存文件
        messages = {
            "title": "保存文件",
            "content": "需要先保存路网文件",
            "yes": "保存",
        }
        confirm = Tools.show_confirm_dialog(messages)
        if confirm == QMessageBox.Yes:
            # 保存路网
            netiface.saveRoadNet()
        else:
            return

        # 4.选择保存模式
        while True:
            messages = {
                "title": "选择文件",
                "content": "请选择简化后的路网覆盖原文件还是另存为新文件",
                "yes": "覆盖原文件",
                "no": "另存为新文件"
            }
            confirm = Tools.show_confirm_dialog(messages)
            if confirm == QMessageBox.Cancel:
                return
            # 获取文件路径
            netFilePath = netiface.netFilePath()
            if confirm == QMessageBox.Yes:
                file_path = netFilePath
                break
            else:
                # 获取保存文件的路径
                file_path = Tools.save_file(("TESSNG", "tess"))
                if not file_path:
                    continue
                # 将源文件复制再进行操作
                shutil.copy(netFilePath, file_path)

        # 5.执行简化
        angle = float(self.lineEdit_angle.text())
        length = float(self.lineEdit_length.text())
        state, message = link_edit.simplifyTessngFile(netiface, file_path, angle, length)

        # 6.显示信息
        if state:
            Tools.show_info_box("路网简化完成")
            Logger.logger_network.info("The simplification of network has been finished:\n" + message)
        else:
            Tools.show_info_box(message, "warning")


# 4.导出车辆轨迹
class TrajectoryExport(QWidget):
    memory_params = {
        "is_coord": False,
        "is_json": False,
        "is_kafka": False,
        "coord_lon": None,
        "coord_lat": None,
        "json_path": Tools.default_traj_json_path,
        "kafka_ip": None,
        "kafka_port": None,
        "kafka_topic": None
    }

    def __init__(self):
        super().__init__()
        self.name = "轨迹数据导出"
        self.width = 300
        self.height = 500

        # kafka有无问题
        self.kafka_is_ok = False

        # 设置界面属性
        Tools.set_attribution(self)
        # 设置界面布局
        self.set_layout()

        # 创建默认保存文件夹
        if not os.path.exists(Tools.default_traj_json_path):
            os.makedirs(Tools.default_traj_json_path, exist_ok=True)

    # 设置界面布局
    def set_layout(self):
        self.file_proj_string, file_proj_info = Tools.read_file_proj()

        # 第一行：勾选框
        self.checkBox_coord = QCheckBox('写入经纬度坐标')
        # 第二行：单选框
        self.radio_proj_file = QRadioButton('使用路网创建时的投影')
        # 第三行：文本
        self.label_proj_file = QLabel(file_proj_info)
        # 第四行：单选框
        self.radio_proj_custom = QRadioButton('使用自定义高斯克吕格投影')
        # 第五行：文本和输入框，使用水平布局
        self.label_proj_custom_lon = QLabel('投影中心经度：')
        self.lineEdit_proj_custom_lon = QLineEdit()
        horizontal_layout_lon = QHBoxLayout()
        horizontal_layout_lon.addWidget(self.label_proj_custom_lon)
        horizontal_layout_lon.addWidget(self.lineEdit_proj_custom_lon)
        # 第六行：文本和输入框，使用水平布局
        self.label_proj_custom_lat = QLabel('投影中心纬度：')
        self.lineEdit_proj_custom_lat = QLineEdit()
        horizontal_layout_lat = QHBoxLayout()
        horizontal_layout_lat.addWidget(self.label_proj_custom_lat)
        horizontal_layout_lat.addWidget(self.lineEdit_proj_custom_lat)
        # 第七行：勾选框
        self.checkBox_json = QCheckBox('保存为Json文件')
        # 第八行：文本和按钮
        self.lineEdit_json = QLineEdit()
        self.lineEdit_json.setFixedWidth(500)
        self.button_json_save = QPushButton('选择保存位置')
        horizontal_layout_json = QHBoxLayout()
        horizontal_layout_json.addWidget(self.lineEdit_json)
        horizontal_layout_json.addWidget(self.button_json_save)
        # 第九行：勾选框
        self.checkBox_kafka = QCheckBox('上传至kafka')
        # 第十行：文本和输入框
        self.label_kafka_ip = QLabel('IP：')
        self.lineEdit_kafka_ip = QLineEdit()
        self.label_kafka_port = QLabel('端口：')
        self.lineEdit_kafka_port = QLineEdit()
        horizontal_layout_kafka_ip = QHBoxLayout()
        horizontal_layout_kafka_ip.addWidget(self.label_kafka_ip)
        horizontal_layout_kafka_ip.addWidget(self.lineEdit_kafka_ip)
        horizontal_layout_kafka_ip.addWidget(self.label_kafka_port)
        horizontal_layout_kafka_ip.addWidget(self.lineEdit_kafka_port)
        # 第十一行：文本和输入框
        self.label_kafka_topic = QLabel('topic：')
        self.lineEdit_kafka_topic = QLineEdit()
        self.button_check_kafka = QPushButton('核验')
        self.label_check_info = QLabel('待核验')
        horizontal_layout_kafka_topic = QHBoxLayout()
        horizontal_layout_kafka_topic.addWidget(self.label_kafka_topic)
        horizontal_layout_kafka_topic.addWidget(self.lineEdit_kafka_topic)
        horizontal_layout_kafka_topic.addWidget(self.button_check_kafka)
        horizontal_layout_kafka_topic.addWidget(self.label_check_info)
        # 第十二行：按钮
        self.button = QPushButton('确定')

        # 限制输入框内容
        validator_coord = QDoubleValidator()
        self.lineEdit_proj_custom_lon.setValidator(validator_coord)
        self.lineEdit_proj_custom_lat.setValidator(validator_coord)
        validator_kafka_port = QIntValidator()
        self.lineEdit_kafka_port.setValidator(validator_kafka_port)
        regex = QRegExp("^[a-zA-Z][a-zA-Z0-9_]*$")
        validator_kafka_topic = QRegExpValidator(regex)
        self.lineEdit_kafka_topic.setValidator(validator_kafka_topic)

        # Box布局 坐标
        group_box_coord = QGroupBox()
        group_box_coord_layout = QVBoxLayout()
        group_box_coord_layout.addWidget(self.radio_proj_file)
        group_box_coord_layout.addWidget(self.label_proj_file)
        group_box_coord_layout.addWidget(self.radio_proj_custom)
        group_box_coord_layout.addLayout(horizontal_layout_lon)
        group_box_coord_layout.addLayout(horizontal_layout_lat)
        group_box_coord.setLayout(group_box_coord_layout)

        # Box布局 Json
        group_box_json = QGroupBox()
        group_box_json_layout = QVBoxLayout()
        group_box_json_layout.addLayout(horizontal_layout_json)
        group_box_json.setLayout(group_box_json_layout)

        # Box布局 kafka
        group_box_kafka = QGroupBox()
        group_box_kafka_layout = QVBoxLayout()
        group_box_kafka_layout.addLayout(horizontal_layout_kafka_ip)
        group_box_kafka_layout.addLayout(horizontal_layout_kafka_topic)
        group_box_kafka.setLayout(group_box_kafka_layout)

        # 总体布局
        layout = QVBoxLayout()
        layout.addWidget(self.checkBox_coord)
        layout.addWidget(group_box_coord)
        layout.addWidget(self.checkBox_json)
        layout.addWidget(group_box_json)
        layout.addWidget(self.checkBox_kafka)
        layout.addWidget(group_box_kafka)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 设置关联关系
        # 监测组件变动
        self.checkBox_coord.stateChanged.connect(self.monitor_state)
        self.radio_proj_custom.toggled.connect(self.monitor_state)
        self.lineEdit_proj_custom_lon.textChanged.connect(self.monitor_state)
        self.lineEdit_proj_custom_lat.textChanged.connect(self.monitor_state)
        self.checkBox_json.stateChanged.connect(self.monitor_state)
        self.lineEdit_json.textChanged.connect(self.monitor_state)
        self.checkBox_kafka.stateChanged.connect(self.monitor_state)
        self.lineEdit_kafka_ip.textChanged.connect(self.monitor_state)
        self.lineEdit_kafka_port.textChanged.connect(self.monitor_state)
        self.lineEdit_kafka_topic.textChanged.connect(self.monitor_state)
        self.lineEdit_kafka_ip.textChanged.connect(self.monitor_kafka)
        self.lineEdit_kafka_port.textChanged.connect(self.monitor_kafka)
        # 关联按钮与调用函数
        self.button_json_save.clicked.connect(self.select_folder)
        self.button_check_kafka.clicked.connect(self.check_kafka)
        self.button.clicked.connect(self.save_config)

        # 设置默认模式和初始状态
        if TrajectoryExport.memory_params["is_coord"]:
            self.checkBox_coord.setChecked(True)
        if TrajectoryExport.memory_params["is_json"]:
            self.checkBox_json.setChecked(True)
        if TrajectoryExport.memory_params["is_kafka"]:
            self.checkBox_kafka.setChecked(True)
        if TrajectoryExport.memory_params["coord_lon"] is not None:
            self.lineEdit_proj_custom_lon.setText(str(TrajectoryExport.memory_params["coord_lon"]))
            self.lineEdit_proj_custom_lat.setText(str(TrajectoryExport.memory_params["coord_lat"]))
        if TrajectoryExport.memory_params["json_path"] is not None:
            self.lineEdit_json.setText(TrajectoryExport.memory_params["json_path"])
        if TrajectoryExport.memory_params["kafka_ip"] is not None:
            self.lineEdit_kafka_ip.setText(str(TrajectoryExport.memory_params["kafka_ip"]))
            self.lineEdit_kafka_port.setText(str(TrajectoryExport.memory_params["kafka_port"]))
            self.lineEdit_kafka_topic.setText(str(TrajectoryExport.memory_params["kafka_topic"]))
        # 投影
        if bool(self.file_proj_string):
            self.radio_proj_file.setChecked(True)
        else:
            self.radio_proj_custom.setChecked(True)
        self.monitor_state()

    # 监测各组件状态，切换控件的可用状态
    def monitor_state(self):
        # 勾选框的状态
        enabled_checkBox_coord = self.checkBox_coord.isChecked()
        # 文件投影的状态
        enabled_proj_file = bool(self.file_proj_string)
        # 选择投影方式的状态
        enabled_radio_proj = self.radio_proj_custom.isChecked()

        # 设置可用状态
        self.radio_proj_file.setEnabled(enabled_checkBox_coord and enabled_proj_file)
        self.label_proj_file.setEnabled(enabled_checkBox_coord and enabled_proj_file and not enabled_radio_proj)
        self.radio_proj_custom.setEnabled(enabled_checkBox_coord)
        self.label_proj_custom_lon.setEnabled(enabled_checkBox_coord and enabled_radio_proj)
        self.label_proj_custom_lat.setEnabled(enabled_checkBox_coord and enabled_radio_proj)
        self.lineEdit_proj_custom_lon.setEnabled(enabled_checkBox_coord and enabled_radio_proj)
        self.lineEdit_proj_custom_lat.setEnabled(enabled_checkBox_coord and enabled_radio_proj)

        ##############################

        # 勾选框的状态
        enabled_checkBox_json = self.checkBox_json.isChecked()

        # 设置可用状态
        self.lineEdit_json.setEnabled(enabled_checkBox_json)
        self.button_json_save.setEnabled(enabled_checkBox_json)

        ##############################

        # 勾选框的状态
        enabled_checkBox_kafka = self.checkBox_kafka.isChecked()

        # 设置可用状态
        self.label_kafka_ip.setEnabled(enabled_checkBox_kafka)
        self.lineEdit_kafka_ip.setEnabled(enabled_checkBox_kafka)
        self.label_kafka_port.setEnabled(enabled_checkBox_kafka)
        self.lineEdit_kafka_port.setEnabled(enabled_checkBox_kafka)
        self.label_kafka_topic.setEnabled(enabled_checkBox_kafka)
        self.lineEdit_kafka_topic.setEnabled(enabled_checkBox_kafka)
        self.button_check_kafka.setEnabled(enabled_checkBox_kafka)
        self.label_check_info.setEnabled(enabled_checkBox_kafka)

        ##############################

        # 设置按钮可用状态
        proj_state = False
        if not enabled_checkBox_coord:
            proj_state = True
        elif enabled_checkBox_coord and not enabled_radio_proj and enabled_proj_file:
            proj_state = True
        elif enabled_checkBox_coord and enabled_radio_proj:
            lon_0 = self.lineEdit_proj_custom_lon.text()
            lat_0 = self.lineEdit_proj_custom_lat.text()
            if lon_0 and lat_0 and -180 < float(lon_0) < 180 and -90 < float(lat_0) < 90:
                proj_state = True

        # json有无问题
        folder_path = self.lineEdit_json.text()
        isdir = os.path.isdir(folder_path)
        json_state = (not enabled_checkBox_json) or (enabled_checkBox_json and isdir)
        if not (enabled_checkBox_json and isdir):
            GlobalVar.traj_json_config = None

        # kafka有无问题
        kafka_state = (not enabled_checkBox_kafka) or (enabled_checkBox_kafka and self.kafka_is_ok)

        # 三个都没问题
        self.button.setEnabled(proj_state and json_state and kafka_state)

    # 监测各组件状态，切换控件的可用状态
    def monitor_kafka(self):
        self.kafka_is_ok = False
        self.label_check_info.setText("待核验")
        # 更新状态
        self.monitor_state()

    # 选择JSON保存文件夹
    def select_folder(self):
        folder_path = Tools.open_folder()
        if folder_path:
            # 显示文件路径在LineEdit中
            self.lineEdit_json.setText(folder_path)

    # 核验kafka
    def check_kafka(self):
        self.label_check_info.setText("核验中…")
        # 立刻更新界面
        QCoreApplication.processEvents()

        ip = self.lineEdit_kafka_ip.text()
        port = self.lineEdit_kafka_port.text()
        topic = self.lineEdit_kafka_topic.text()

        # 核验IP
        ip_is_ok = False
        if ip:
            try:
                ip_address(ip)
                ip_is_ok = True
            except:
                Tools.show_info_box("请输入正确的IPv4地址", "warning")
                return
        else:
            Tools.show_info_box("请输入IPv4地址", "warning")
            return
        # 核验端口
        port_is_ok = False
        if port:
            if int(port) > 0:
                port_is_ok = True
            else:
                Tools.show_info_box("请输入大于0的端口号", "warning")
                return
        else:
            Tools.show_info_box("请输入端口号", "warning")
            return
        # 核验topic
        topic_is_ok = False
        if topic:
            topic_is_ok = True
        else:
            Tools.show_info_box("请输入topic", "warning")
            return

        kafka_pull_is_ok = self.check_kafka_pull(ip, port)

        # 如果都没问题
        if ip_is_ok and port_is_ok and topic_is_ok and kafka_pull_is_ok:
            self.kafka_is_ok = True
            self.label_check_info.setText("核验成功")
        else:
            self.kafka_is_ok = False
            self.label_check_info.setText("核验失败")

        # 更新状态
        self.monitor_state()

    # 核查kafka连通性
    def check_kafka_pull(self, ip, port):
        test_topic = "pytessng_test"
        kafka_pull_is_ok = False

        try:
            # 创建 KafkaProducer 实例，用于发送测试消息
            producer = KafkaProducer(
                bootstrap_servers=f'{ip}:{port}',
                acks=1,  # 确认级别 1 表示 leader 收到消息即确认
                retries=5,
                max_in_flight_requests_per_connection=1,
            )
            # 发送测试消息到指定 topic
            producer.send(test_topic, b'test_message')
            producer.flush()

            # 创建 KafkaConsumer 实例，用于拉取消息
            consumer = KafkaConsumer(
                test_topic,
                bootstrap_servers=f'{ip}:{port}',
                group_id='test_group',
                auto_offset_reset='earliest',
                enable_auto_commit=False,
                consumer_timeout_ms=5000  # 设置拉取消息的超时时间
            )
            # 订阅topic并拉取消息
            for _ in consumer:
                Logger.logger_network.info(f"Kafka can receive messages.")
                kafka_pull_is_ok = True
                message = "Kafka connectivity test successful!"
                Logger.logger_network.info(message)
                break
        except:
            message = f"Kafka connectivity test failed with the following error:\n{traceback.format_exc()}"
            Logger.logger_network.error(message)
        try:
            consumer.close()
        except:
            pass

        return kafka_pull_is_ok

    # 确认键
    def save_config(self):
        # 获取投影
        if self.checkBox_coord.isChecked():
            TrajectoryExport.memory_params["is_coord"] = True
            if self.radio_proj_custom.isChecked():
                lon_0 = float(self.lineEdit_proj_custom_lon.text())
                lat_0 = float(self.lineEdit_proj_custom_lat.text())
                TrajectoryExport.memory_params["coord_lon"] = lon_0
                TrajectoryExport.memory_params["coord_lat"] = lat_0
                traj_proj_string = f'+proj=tmerc +lon_0={lon_0} +lat_0={lat_0} +ellps=WGS84'
            else:
                traj_proj_string = self.file_proj_string
        else:
            TrajectoryExport.memory_params["is_coord"] = False
            traj_proj_string = ""

        if self.checkBox_json.isChecked():
            TrajectoryExport.memory_params["is_json"] = True
            traj_json_config = self.lineEdit_json.text()
            TrajectoryExport.memory_params["json_path"] = traj_json_config
        else:
            TrajectoryExport.memory_params["is_json"] = False
            traj_json_config = None

        if self.checkBox_kafka.isChecked() and self.kafka_is_ok:
            TrajectoryExport.memory_params["is_kafka"] = True
            ip = self.lineEdit_kafka_ip.text()
            port = self.lineEdit_kafka_port.text()
            topic = self.lineEdit_kafka_topic.text()
            traj_kafka_config = {
                "ip": ip,
                "port": port,
                "topic": topic
            }
            TrajectoryExport.memory_params["kafka_ip"] = ip
            TrajectoryExport.memory_params["kafka_port"] = port
            TrajectoryExport.memory_params["kafka_topic"] = topic
        else:
            TrajectoryExport.memory_params["is_kafka"] = False
            traj_kafka_config = None

        # 配置全局变量
        GlobalVar.traj_proj_string = traj_proj_string
        GlobalVar.traj_json_config = traj_json_config
        GlobalVar.traj_kafka_config = traj_kafka_config

        # 关闭窗口
        self.close()


# 5.3.提出建议
class SendAdvise(QWidget):
    def __init__(self):
        super().__init__()
        self.name = "提交用户反馈"
        self.width = 300
        self.height = 150

        # 设置界面属性
        Tools.set_attribution(self)
        # 设置界面布局
        self.set_layout()

    # 设置界面布局
    def set_layout(self):
        # 第一行：文本
        self.label = QLabel('感谢您使用TESS NG系列产品，欢迎您提出宝贵的建议和意见！')
        # 第二行：输入框
        self.textEdit = QTextEdit()
        self.textEdit.setFixedHeight(5 * self.textEdit.fontMetrics().height())
        # 第三行：按钮
        self.button = QPushButton('提交')

        # 总体布局
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.textEdit)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 监测组件变动
        self.textEdit.textChanged.connect(self.monitor_state)
        # 关联按钮与调用函数
        self.button.clicked.connect(self.send_advise)
        # 设置默认状态
        self.button.setEnabled(False)

    def monitor_state(self):
        text = self.textEdit.toPlainText()
        self.button.setEnabled(bool(text))

    def send_advise(self):
        text = self.textEdit.toPlainText()
        status_code = Tools.send_message("suggestion", text)
        if status_code == 201:
            message = "提交成功，感谢您的反馈！"
        else:
            message = "感谢您的反馈！"
        # 关闭窗口
        self.close()
        # 提示信息
        Tools.show_info_box(message)



