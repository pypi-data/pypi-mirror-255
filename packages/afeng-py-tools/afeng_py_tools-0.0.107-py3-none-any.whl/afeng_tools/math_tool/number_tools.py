"""
数字工具：
1、可以使用模块：pip install cn2an
    将字符串中的数字转为汉字： cn2an.transform(str_data, "an2cn")

"""
from afeng_tools.math_tool.core import number_to_chinese


def num_to_chinese(num_value: int):
    """数字转中文"""
    try:
        import cn2an
        return number_to_chinese.num_to_chinese(num_value)
    except Exception:
        return number_to_chinese.to_chinese(num_value)
