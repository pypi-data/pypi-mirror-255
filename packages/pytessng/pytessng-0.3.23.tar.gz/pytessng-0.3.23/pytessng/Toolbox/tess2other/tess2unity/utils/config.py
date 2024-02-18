# 场景比例尺
sceneScale = 1

# unity 属性映射关系
convert_attribute_mapping = {
    "black": "Driving",
    "white": "WhiteLine",
    "yellow": "YellowLine",
}

filter_ids = []
border_line_width = 0.2
center_line_width = 0.3
empty_line_lenfth, real_line_length = 3, 4  # 虚实线长度

# # unity 信息提取的类型映射
# UNITY_LANE_MAPPING = {
#     "Driving": ["driving", "stop", "parking", "entry", "exit", "offRamp", "onRamp", "connectingRamp", ],
#     "None": ["none"],
#     "GreenBelt": ["shoulder", "border", "median", "curb"],
#     "SideWalk": ["sidewalk"],
#     "Biking": ["biking", ],
#     "Restricted": ["restricted"],
#     "WhiteLine": [],
#     "YellowLine": [],
#     "Other": ["bidirectional", "special1", "special2", "special3", "roadWorks", "tram", "rail", ]
# }

# 为了节省空间，仅对路段级的做黑色三角形，同时取车道左侧做白色线，一般为白色虚线，如果车道类型不一致，做白色实线，如果是最左侧车道，做黄色实线
