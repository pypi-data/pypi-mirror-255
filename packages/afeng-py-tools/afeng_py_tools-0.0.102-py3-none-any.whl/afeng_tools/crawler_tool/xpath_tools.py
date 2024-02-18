"""
xpath工具： 安装：pip install lxml -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""

from lxml import etree


def get_html_tree(html_file: str):
    """转换html文件为html_tree"""
    parser = etree.HTMLParser(encoding="utf-8")
    return etree.parse(html_file, parser=parser)


def parse_to_html_tree(html_text: str):
    """转换字符串为html_tree"""
    return etree.HTML(html_text)
