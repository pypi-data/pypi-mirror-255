from functools import partial
from PySide2.QtWidgets import QMenu, QAction
from PySide2.QtCore import Qt

from ..DLLs.Tessng import PyCustomerNet, tessngIFace
from ..Tessng.MyMenu import GlobalVar


class MyNet(PyCustomerNet):
    def __init__(self):
        super(MyNet, self).__init__()

        # 用于打断路段的菜单栏
        self.context_menu_split_link = None

    def afterLoadNet(self):
        iface = tessngIFace()
        netiface = iface.netInterface()
        # 网格化
        netiface.buildNetGrid(5)
        # 能执行这里说明是正版key，开启相关功能
        if self.action_network_edit_split is not None:
            self.action_network_edit_split.setEnabled(True)
        self.action_trajectory_export.setEnabled(True)

        # 打印属性信息
        attrs = netiface.netAttrs().otherAttrs()
        print("=" * 66)
        print("Load network! Network attrs:")
        if attrs:
            for k, v in attrs.items():
                print(f"\t{k:<15}:{' '*5}{v}")
        else:
            print("\t(EMPTY)")
        print("=" * 66, "\n")


    # 鼠标点击
    def afterViewMousePressEvent(self, event):
        iface = tessngIFace()
        guiiface = iface.guiInterface()
        netiface = iface.netInterface()

        if GlobalVar.is_need_split_link:
            # 将按钮修改成【取消工具】
            guiiface.actionNullGMapTool().trigger()
            # 如果是右击
            if event.button() == Qt.RightButton:
                # 网格化
                netiface.buildNetGrid(5)
                # 在TESSNG中的坐标
                pos = netiface.graphicsView().mapToScene(event.pos())
                # 找到一定距离之内的车道所在路段的ID
                all_link_id = []
                for location in netiface.locateOnCrid(pos, 9):
                    dist = location.leastDist
                    if dist < 4:
                        try:
                            lane = location.pLaneObject
                            link_id = int(lane.link().id())
                            all_link_id.append(link_id)
                        except:
                            pass
                all_link_id = sorted(set(all_link_id))
                # 获取界面
                win = guiiface.mainWindow()
                # 创建菜单栏
                self.context_menu_split_link = QMenu(win)
                # 在菜单中添加动作
                for link_id in all_link_id:
                    action = QAction(f"打断路段{link_id}", win)
                    action.triggered.connect(partial(self.split_link, link_id, pos))
                    self.context_menu_split_link.addAction(action)
                self.context_menu_split_link.addAction(GlobalVar.action_split_link)
                # 设置右击事件
                win.setContextMenuPolicy(Qt.CustomContextMenu)
                win.customContextMenuRequested.connect(self.show_context_menu_split_link)

    # 在鼠标位置显示菜单
    def show_context_menu_split_link(self, pos):
        if not GlobalVar.is_need_split_link:
            return
        if self.context_menu_split_link is None:
            return
        iface = tessngIFace()
        win = iface.guiInterface().mainWindow()
        self.context_menu_split_link.exec_(win.mapToGlobal(pos))

    # 打断路段
    def split_link(self, link_id, pos):
        # 获取打断信息
        from pytessng.Toolbox.link_edit import link_edit

        iface = tessngIFace()
        netiface = iface.netInterface()
        x, y = pos.x(), -pos.y()
        link_edit.splitLink(netiface, link_id, (x,y))

        # 关闭菜单
        self.context_menu_split_link.close()
        self.context_menu_split_link = None


    # 控制元素绘制
    def isPermitForCustDraw(self):
        return True

    # 控制路段颜色
    def linkBrushColor(self, id, color):
        if GlobalVar.link_color:
            if id in GlobalVar.link_color["1"]:
                color.setNamedColor("#000000")
                return True
            elif id in GlobalVar.link_color["2"]:
                color.setNamedColor("#000000")
                # color.setNamedColor("#AAAAAA")
                return True
        return False


    # 控制曲率最小距离
    def ref_curvatureMinDist(self, itemType: int, itemId: int, ref_minDist):
        ref_minDist.value = 0.1
        return True

