"""
泛型工具
"""
import sys

py_version = sys.version_info
if py_version >= (3, 8):
    from typing import get_args, TypeVar


def get_generic_type_arg(cls, arg_index: int = 0):
    """获取泛型值"""
    t = cls.__orig_bases__[0]
    if py_version >= (3, 8):
        return get_args(t)[arg_index]
    else:
        return t.__args__[arg_index]


def get_generic_type(cls, arg_index: int = 0):
    """获取泛型类型"""
    generic_type = get_generic_type_arg(cls, arg_index)
    if isinstance(generic_type, TypeVar):
        return cls.model_type
    return generic_type
