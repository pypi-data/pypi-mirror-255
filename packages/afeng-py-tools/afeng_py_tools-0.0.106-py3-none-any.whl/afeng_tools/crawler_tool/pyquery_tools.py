"""
使用PyQyery操作HTML： http://pyquery.readthedocs.io/en/latest/api.html
    安装：pip install lxml -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
         pip install pyquery -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
from pyquery import PyQuery


def get_PyQuery_from_url(url: str) -> PyQuery:
    """获取PyQuery（通过url）"""
    return PyQuery(url=url)


def get_PyQuery_from_html(html_content: str) -> PyQuery:
    """获取PyQuery（通过html内容）"""
    return PyQuery(html_content)


def get_PyQuery_from_file(html_file: str, encoding: str = "utf-8") -> PyQuery:
    """获取PyQuery（通过html文件）"""
    return PyQuery(filename=html_file, encoding=encoding)


def get_PyQuery(html_content: str = None, url: str = None, html_file: str = None, encoding: str = "utf-8"):
    """获取PyQuery"""
    if url is not None:
        return get_PyQuery_from_url(url)
    elif html_file is not None:
        return get_PyQuery_from_file(html_file, encoding=encoding)
    else:
        return get_PyQuery_from_html(html_content)


def query(dom: PyQuery, css_selector) -> PyQuery:
    """通过[css选择器/伪类选择器]查询元素"""
    return dom(css_selector)


def find(el: PyQuery, css_selector) -> PyQuery:
    """通过[css选择器/伪类选择器]查找当前节点的子节点"""
    return el.find(css_selector)


def children(el: PyQuery, css_selector: str = None) -> PyQuery:
    """通过[css选择器/伪类选择器]获取当前节点的直接子节点"""
    if css_selector is None:
        return el.children()
    return el.children(css_selector)


def parent(el: PyQuery) -> PyQuery:
    """通过[css选择器/伪类选择器]获取当前节点的直接父亲节点"""
    return el.parent()


def parents(el: PyQuery, css_selector: str = None) -> PyQuery:
    """通过[css选择器/伪类选择器]获取当前节点的所有祖宗节点"""
    if css_selector is None:
        return el.parents()
    return el.parents(css_selector)


def siblings(el: PyQuery, css_selector: str = None) -> PyQuery:
    """通过[css选择器/伪类选择器]获取当前节点的兄弟节点"""
    if css_selector is None:
        return el.siblings()
    return el.siblings(css_selector)


def set_html(el: PyQuery, value: str) -> PyQuery:
    """获取元素的html内容"""
    return el.html(value)


def get_html(el: PyQuery) -> str:
    """获取元素的html内容"""
    return el.html()


def set_text(el: PyQuery, value: str) -> PyQuery:
    """获取元素的text文本"""
    return el.text(value)


def get_text(el: PyQuery) -> str:
    """获取元素的text文本"""
    return el.text()


def get_attr(el: PyQuery, attr_name: str) -> str:
    """获取元素的属性值"""
    return el.attr(attr_name)


def set_attr(el: PyQuery, attr_name: str, attr_value: str) -> PyQuery:
    """设置元素的属性值"""
    return el.attr(attr_name, attr_value)


def get_items(el: PyQuery) -> list[PyQuery]:
    """获取元素列表项"""
    return el.items()


def add_class(el: PyQuery, class_value) -> PyQuery:
    """添加class"""
    return el.add_class(class_value)


def remove_class(el: PyQuery, class_value) -> PyQuery:
    """移除class"""
    return el.remove_class(class_value)


def add_style(el: PyQuery, css_field: str, css_value: str) -> PyQuery:
    """
    添加style样式
    :param el:
    :param css_field: 如：‘font-size’
    :param css_value: 如：14px
    :return: PyQuery
    """
    return el.css(css_field, css_value)


def remove_el(el: PyQuery):
    """移除元素"""
    return el.remove()
