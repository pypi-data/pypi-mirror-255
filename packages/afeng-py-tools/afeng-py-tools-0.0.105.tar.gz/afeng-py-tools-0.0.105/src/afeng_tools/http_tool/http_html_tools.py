"""
html内容工具类
"""
import re


def replace_image_tag_delay_src(html_content):
    """转换图片标签的src"""
    if html_content:
        img_tag_pattern = '<img(.*?) src="(.*?)"(.*?)>'
        return re.sub(img_tag_pattern,
                      lambda m: f'<img{m.group(1)} data-src="{m.group(2)}"{m.group(3)}>',
                      html_content)