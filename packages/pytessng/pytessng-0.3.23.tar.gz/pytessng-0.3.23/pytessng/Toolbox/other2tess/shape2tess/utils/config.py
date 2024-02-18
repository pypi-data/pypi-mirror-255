# 比例尺
sceneScale = 1

# 投影函数
p = None

# 车道默认宽度
default_lane_width = {
    "driving": 3.5,
    "biking": 1.5,
    "sidewalk": 1.5,
    "stop": 3.5
    }

# 小于该宽度的路段要删除
min_width = 2.5

# 车道类型
LANE_TYPE_MAPPING = {
    'driving': '机动车道',
    'biking': '非机动车道',
    'sidewalk': '非机动车道',  # 行人道实际无意义
    'stop': '应急车道',
    }

# 寻点距离
join_point_distance = 2.8

# 检查最长的车道与最短的车道的长度差是否在一定范围内
threshold_length = 20 # m

# 各条车道的起终点距离上下限
threshold_distance_max = 9 # m
threshold_distance_min = 0 # m
