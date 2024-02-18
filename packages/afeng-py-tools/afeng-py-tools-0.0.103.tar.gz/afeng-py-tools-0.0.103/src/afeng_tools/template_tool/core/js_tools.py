"""
js工具
- 压缩js: pip install jsmin -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
    - https://pypi.org/project/jsmin/
    -
-
"""
from jsmin import jsmin


def min_js(js_content: str) -> str:
    """
    压缩js
    :param js_content: js内容
    :return:
    """
    return jsmin(js_content, quote_chars="'\"`")


def min_js_file(js_file: str) -> str:
    """
    压缩js
    :param js_file: js文件
    :return:
    """
    with open(js_file) as js_file:
        return jsmin(js_file.read(), quote_chars="'\"`")


def wrap_js(js_var_name, js_var_fun_code: str) -> str:
    """
    包装js
    :param js_var_name: js变量名, 如：factorial
    :param js_var_fun_code: js函数代码 如：
    ... function(n) {
    ...    if (n < 1)
    ...       throw new Error('factorial where n < 1 not supported');
    ...     else if (n == 1)
    ...       return 1;
    ...     else
    ...       return n * factorial(n - 1);
    ... }
    :return: 包装后的js代码，可以使用如下方式使用： var value = window.factorial(5); console.log('the value is ' + value);
    """
    return '(function(root) { root.'+js_var_name+' = '+js_var_fun_code+' })(window);'
