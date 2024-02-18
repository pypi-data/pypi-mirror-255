import os
from datetime import datetime
import pandas as pd
from .....Tessng.MyMenu import ProgressDialog as pgd


# 获取路段信息
def get_data(file_path):
    # 获取文件后缀
    _, extension = os.path.splitext(file_path)
    # 读取文件
    if extension == ".csv":
        try:
            data = pd.read_csv(file_path, encoding="utf-8")
        except:
            data = pd.read_csv(file_path, encoding="gbk")
    elif extension in [".xlsx", ".xls"]:
        data = pd.read_excel(file_path)
    else:
        raise Exception("Invaild file format!")

    # 保存路段信息
    links_data = {}
    ID = 1
    xs, ys = [], []
    for col in pgd.progress(data.to_numpy(), '路段数据解析中（1/2）'):
        link_name = col[0] if col[0] else ID
        link_count = int(col[1])
        link_points = [list(map(float, j.split(","))) for j in col[2:] if str(j) != "nan"]
        links_data[ID] = {
            "link_name": link_name,
            "link_count": link_count,
            "link_points": link_points
        }
        ID += 1
        # 记录x和y
        xs.extend([p[0] for p in link_points])
        ys.extend([p[1] for p in link_points])

    # 找到中心位置，记录move
    if xs and ys:
        x_center = (min(xs) + max(xs)) / 2
        y_center = (min(ys) + max(ys)) / 2
    else:
        x_center = 0
        y_center = 0

    # 其他信息
    other_data = {
        "data_source": "Excel",
        "created_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "move_distance": {
            "x_move": -round(x_center, 3),
            "y_move": -round(y_center, 3)
        }
    }

    return links_data, other_data