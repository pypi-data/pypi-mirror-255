"""
模板装饰器工具
"""
from typing import Callable

from afeng_tools.decorator_tool import decorator_tools


def html_template(name: str, file: str):
    """装饰器：html模板"""
    def func_wrapper(func: Callable):
        def inner_wrapper(*args, **kwargs):
            if 'template_name' not in kwargs:
                kwargs['template_name'] = name
            if 'template_file' not in kwargs:
                kwargs['template_file'] = file
            return decorator_tools.run_func(func, *args, **kwargs)
        return inner_wrapper
    return func_wrapper
