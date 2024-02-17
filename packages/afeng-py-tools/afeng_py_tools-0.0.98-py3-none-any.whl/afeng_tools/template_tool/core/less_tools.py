"""
less工具：pip install lesscpy -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
- https://pypi.org/project/lesscpy/
"""
import os

import lesscpy
from io import StringIO


def compile_less(less_str: str, minify: bool = True):
    return lesscpy.compile(StringIO(less_str), minify=minify)


def compile_to_css(less_code: str, less_dir: str = None, minify: bool = True):
    """
    less转css
    :param less_code: less代码
    :param less_dir: less文件所在目录
    :param minify: 是否压缩
    :return: css代码
    """
    old_work_dir = os.getcwd()
    if less_dir and '@import ' in less_code:
        # 改变当前路径为less的路径
        os.chdir(less_dir)
    result = lesscpy.compile(StringIO(less_code), minify=minify)
    os.chdir(old_work_dir)
    return result
