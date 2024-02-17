"""
jinja2模板装饰器
"""
from functools import wraps

from afeng_tools.decorator_tool import decorator_tools


def jinja2_filter(name: str):
    """jinja2过滤器装饰器(name为jinja2模板中使用到的过滤器名)"""
    def func_wrap(func):
        decorator_tools.append_decorator_info(func, 'jinja2_filter')
        decorator_tools.append_func_info(func, '__filter_name__', name)

        @wraps(func)
        def inner_wrap(*args, **kwargs):
            return decorator_tools.run_func(func, *args, **kwargs)
        return inner_wrap
    return func_wrap
