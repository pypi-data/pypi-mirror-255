"""
pickle序列化与反序列化工具
"""
import pickle


def save_to_file(obj_list: list[object], save_file: str):
    """保存到文件"""
    with open(save_file, "wb") as f:
        # 序列化
        pickle.dump(len(obj_list), f)
        for tmp_obj in obj_list:
            # 序列化
            pickle.dump(tmp_obj, f)


def parse_to_obj(save_file: str) -> list:
    """保存到文件"""
    with open(save_file, "rb") as f:
        list_size = pickle.load(f)
        # 反序列
        return [pickle.load(f) for tmp in range(list_size)]
