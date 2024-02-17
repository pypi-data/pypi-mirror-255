"""
- pip install beautifulsoup4 -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
- pip install pyquery -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import os.path

from bs4 import BeautifulSoup
from pyquery import PyQuery

from afeng_tools.crawler_tool import pyquery_tools
from afeng_tools.file_tool import file_tools
from afeng_tools.template_tool.core import js_tools, less_tools


def _render_html(html_dom: PyQuery, template_name: str) -> str:
    """渲染html代码"""
    template_type = html_dom("template").attr('type')
    template_value = html_dom("template").attr('value')
    if template_type == 'macro':
        html_dom('template>div:first-child').html(
            html_dom('template>div:first-child').outer_html(method="xml")
        ).attr('class', template_value).remove_attr('id')
    elif template_type == 'macro-child':
        pass
    template_html = html_dom("template").html()
    html_bs = BeautifulSoup(template_html, 'html.parser')
    if template_type == 'macro':
        return html_bs.prettify()
    else:
        return f'<div id="{template_name}">{html_bs.prettify()}</div>'


def _render_js(html_dom: PyQuery, template_name: str, parent_html_dom: PyQuery = None) -> str:
    """渲染js代码"""
    js_list = []
    for item in html_dom('script').items():
        if item.attr('src'):
            js_list.append(item.outer_html())
        else:
            tmp_js_list = list()
            tmp_js_list.append('<script>')
            tmp_js_list.append(js_tools.min_js('var ' + template_name + ' = ' +
                                                  ''.join(item.contents()).strip().lstrip('export')
                                                  .strip().lstrip('default').strip() + ';'))
            tmp_js_list.append(template_name + '.methods.init();')
            tmp_js_list.append('</script>')
            js_list.append(''.join(tmp_js_list))
    parent_js = ''
    if parent_html_dom:
        parent_js = parent_html_dom('script').outer_html()
    return parent_js + ''.join(js_list)


def _render_css(html_dom: PyQuery, template_name: str, less_dir: str) -> str:
    """渲染css代码"""
    template_type = html_dom("template").attr('type')
    template_value = html_dom("template").attr('value')
    parent_style = ''
    style_list = list()
    if template_type == 'macro':
        style_list.append('.' + template_value + '{')
    else:
        style_list.append('#' + template_name + '{')
    for tmp in html_dom('style').contents():
        style_list.append(tmp)
    style_list.append('}')
    return parent_style + str(html_dom('link')) + \
        '<style>' + less_tools.compile_to_css(''.join(style_list), less_dir=less_dir) + '</style>'


def _get_parent_html_dom(html_dom: PyQuery, template_root_path: str):
    template_parent = html_dom("template").attr('parent')
    if template_parent:
        parent_template_file = os.path.join(template_root_path, template_parent)
        if os.path.exists(parent_template_file):
            return pyquery_tools.get_PyQuery_from_html(file_tools.read_file(parent_template_file))


def _render_macro_html(html_dom: PyQuery, html_code: str, js_code: str, css_code: str):
    if html_dom("template").attr('type') == 'macro':
        html_code = html_code.rstrip().rstrip('%}').rstrip().rstrip('endmacro') \
            .rstrip().rstrip('-').rstrip().rstrip('{%')
        html_code = html_code + js_code + css_code
        html_code = html_code + '{%- endmacro %}'
    return html_code


def render(template_file: str, template_root_path: str):
    """
    格式化模板
    :param template_file: 模板文件，类似vue模板
    :param template_root_path: 模板根路径
    :return:(html代码，js代码，css代码)
    """
    html_dom = pyquery_tools.get_PyQuery_from_html(file_tools.read_file(template_file))
    template_name = os.path.split(template_file)[1].rsplit('.', maxsplit=1)[0]
    template_name = template_name.replace('-', '_')
    template_name = 'template_' + template_name
    parent_html_dom = _get_parent_html_dom(html_dom, template_root_path=template_root_path)
    html_code = _render_html(html_dom, template_name)
    html_code = html_code.replace('&gt;', '>').replace('&lt;', '<')
    js_code = _render_js(html_dom, template_name, parent_html_dom)
    css_code = _render_css(html_dom, template_name, os.path.dirname(template_file))
    css_code = css_code.replace(' rem', 'rem')
    html_code = _render_macro_html(html_dom, html_code, js_code, css_code)
    return html_code, js_code, css_code
