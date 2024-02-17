def calculate_relative_value(input_data: list, db_data: list) -> float:
    """计算input_data中db_data所占的比例"""
    # 去重
    input_data_unique: set = set(input_data)
    db_data_unique: set = set(db_data)
    # 获取交集.
    # 获取input_data中db_data的数据
    intersection: set = input_data_unique.intersection(db_data_unique)

    # 获取input_data中db_data所占的比例
    result: float = len(intersection) / len(input_data_unique)
    return result
