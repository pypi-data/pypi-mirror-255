"""
javascript工具：
- pip install py_mini_racer -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""

import json

from py_mini_racer import py_mini_racer

js_racer = py_mini_racer.MiniRacer()


def run_js(js_code: str):
    """执行js代码"""
    return js_racer.eval(js_code)


def run_code(js_code: str, is_fun_wrap: bool = False, return_obj_name: str = None):
    """
    运行js代码
    :param js_code: js代码
    :param is_fun_wrap: 是否使用函数包含js代码
    :param return_obj_name: 返回的对象名
    :return: js运行结果
    """
    if is_fun_wrap:
        js_code = 'function js_run_code(){\n' + js_code
        js_code = js_code + f'\nreturn JSON.stringify({return_obj_name});'
        js_code = js_code + '}\n'
        js_code = js_code + 'js_run_code();'
    result = run_js(js_code)
    return json.loads(result)


def _test_run():
    jscode = """
    function add(a, b){return a + b;} add(1, 2);
    """
    result = run_js(jscode)
    print(result)


def _test_run_code():
    jscode = """
    var test=123456
    """
    result = run_code(jscode, return_obj_name='test')
    print(result)


if __name__ == '__main__':
    _test_run()
    # _test_run_code()
