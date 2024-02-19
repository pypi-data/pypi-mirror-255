"""
jinja2自定义过滤器
"""
import re

from afeng_tools.encryption_tool import hashlib_tools
from afeng_tools.jinja2_tool.jinja2_decorator_tools import jinja2_filter


@jinja2_filter('value')
def filter_none_value(value, default: int | float | str | list | dict = None,
                      is_list: bool = False, is_obj: bool = False):
    if value is None:
        if is_list:
            return default if default is not None else []
        elif is_obj:
            return default if default is not None else dict()
        else:
            return default if default is not None else ''
    return value


@jinja2_filter('md5')
def filter_md5(value):
    if value is None:
        return ''
    result_md5 = hashlib_tools.calc_md5(value)
    re_match = re.match('(\d*).*?', result_md5)
    if re_match:
        result_md5 = result_md5.removeprefix(re_match.group(1))
    return result_md5


if __name__ == '__main__':
    print(filter_md5('测试啊'))
