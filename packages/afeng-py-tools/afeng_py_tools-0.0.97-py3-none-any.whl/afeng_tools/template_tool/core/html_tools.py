"""
html工具：
- 压缩html: pip install htmlmin2 -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
    - https://pypi.org/project/htmlmin2/
    - https://htmlmin.readthedocs.io/en/latest/quickstart.html
-
"""
import htmlmin

def min_html(html_content:str):
    """
    压缩html
    :param html_content: html内容
    :return: 压缩后的html
    """
    return htmlmin.minify(html_content)