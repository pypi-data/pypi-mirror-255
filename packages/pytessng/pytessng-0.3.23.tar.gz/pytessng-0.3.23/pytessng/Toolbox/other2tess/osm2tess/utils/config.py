# 拉取的路段类型
road_class_type = {
    1: ["motorway", "motorway_link"],
    2: [
        "motorway", "motorway_link",
        "trunk", "trunk_link",
        "primary", "primary_link",
        "secondary", "secondary_link",
        "tertiary", "tertiary_link"
    ],
}

# 默认路段类型等级
default_road_class = 3

# 不同道路类型的默认车道数
default_lane_count = {
    "motorway": 3,
    "motorway_link": 2,
    "trunk": 3,
    "trunk_link": 2,
    "primary": 3,
    "primary_link": 1,
    "secondary": 2,
    "secondary_link": 1,
    "tertiary": 2,
    "tertiary_link": 1,
    "other": 1,
    }

# 车道宽度
default_lane_width = 3.5

