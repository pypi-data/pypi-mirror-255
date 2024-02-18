"""
SCSS工具: pip install pyScss -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
- https://pypi.org/project/pyScss/
- https://pyscss.readthedocs.io/en/latest/
"""

from scss import Compiler

scss_compiler = Compiler()


def compile_scss(scss_str: str):
    return scss_compiler.compile_string(scss_str)
