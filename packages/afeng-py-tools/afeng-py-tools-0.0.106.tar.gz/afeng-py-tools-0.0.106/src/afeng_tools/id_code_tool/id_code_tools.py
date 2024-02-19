"""
id和编码工具
"""


def get_code_by_id(id_value: int, begin_value=100000) -> int:
    """通过id获取编码"""
    return begin_value + id_value


def get_id_by_code(code: int, begin_value=100000) -> int:
    """通过编码获取id"""
    return code - begin_value


def get_tmp_pwd(code: int) -> str:
    """获取PWD"""
    if code <= 106603:
        return str(code - 999)[:4]
    return str(int(str(code)[::-1]) + code + 9999)[:4]
