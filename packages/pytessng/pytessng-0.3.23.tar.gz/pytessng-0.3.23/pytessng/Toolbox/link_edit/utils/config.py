sceneScale = 1


# tess 中车道类型定义 机动车道/机非共享/非机动车道/公交专用道
LANE_TYPE_MAPPING = {
    'driving': '机动车道',
    'biking': '非机动车道',
    'sidewalk': '人行道',  # 行人道实际无意义
    'stop': '应急车道',

    # 'onRamp': '机动车道',
    # 'offRamp': '机动车道',
    # 'entry': '机动车道',
    # 'exit': '机动车道',
    # 'connectingRamp': '机动车道',
    # 'shoulder': '应急车道',
    # 'border': '',
    # 'none': '',
    # 'redtricted': '',
    # 'parking': '停车带',
    # 'median': '',
    # 'curb': '',
}

# 当前后几个点的向量夹角小于 default_angle 且点距小于 max_length(除非夹角为0 ) 时，抹除过渡点
default_angle = 1
max_length = 50


# 连续次数后可视为正常车道，或者连续次数后可视为连接段,最小值为2
point_require = 2
POINT_REQUIRE = max(2, point_require)



# 需要被处理的车道类型及处理参数
WIDTH_LIMIT = {
    '机动车道': {
        'split': 2,  # 作为正常的最窄距离
        'join': 1.5,  # 被忽略时的最宽距离
    },
    '非机动车道': {
        'split': 2,
        'join': 0.5,
    },
}

