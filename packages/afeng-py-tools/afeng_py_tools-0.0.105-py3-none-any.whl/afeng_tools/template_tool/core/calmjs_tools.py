"""
calmjs 工具
- 压缩：pip install calmjs.parse -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
from calmjs.parse import es5
from calmjs.parse.unparsers.es5 import minify_print, pretty_print, pretty_printer, minify_printer, Unparser
from calmjs.parse.rules import indent
from calmjs.parse.rules import obfuscate

import json
from io import StringIO
from calmjs.parse.sourcemap import encode_sourcemap, write


def js_minify(js_code: str, obfuscate: bool = False, obfuscate_globals: bool = False):
    """压缩js"""
    program = es5(js_code, with_comments=True)
    return minify_print(program, obfuscate=obfuscate, obfuscate_globals=obfuscate_globals)


def js_pretty(js_code: str, obfuscate: bool = False, obfuscate_globals: bool = False):
    """漂亮打印js"""
    program = es5(js_code, with_comments=True)
    return pretty_print(program, indent_str='    ')


def js_sourcemap(js_code: str, source_js: str, min_js_file: str) -> str:
    """
    js压缩与原js的sourcemap
    :param js_code:
    :param source_js: 源js，如：'demo.js'
    :param min_js_file: 压缩js文件，如：'demo.min.js'
    :return: sourcemap的json字符串
    """
    program = es5(js_code, with_comments=True)
    program.sourcepath = source_js
    stream_m = StringIO()
    print_m = minify_printer(obfuscate=True, obfuscate_globals=True)
    sourcemap_m = encode_sourcemap(min_js_file, *write(print_m(program), stream_m))
    return json.dumps(sourcemap_m, indent=2, sort_keys=True)


def js_obfuscate(js_code: str):
    """
    混淆js代码
    :param js_code:
    :return: 混淆后的代码
    """
    pretty_obfuscate = Unparser(rules=(obfuscate(obfuscate_globals=False), indent(indent_str='    '),))
    math_module = es5(js_code)
    return ''.join(c.text for c in pretty_obfuscate(math_module))


