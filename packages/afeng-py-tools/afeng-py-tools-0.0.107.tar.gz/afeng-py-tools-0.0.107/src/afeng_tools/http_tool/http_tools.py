"""
HTTP工具
- 安装：pip install lxml -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""

from typing import Optional

import requests
from lxml import etree

from afeng_tools.http_tool.decorator.http_auto_retry_tools import auto_retry
from afeng_tools.log_tool.loguru_tools import get_logger

logger = get_logger()


@auto_retry(max_retries=3)
def get_html_text(url, params: Optional[dict] = None, headers: Optional[dict] = None, retry: int = 3, timeout: int = 3000):
    """获取请求得到的响应文本内容"""
    if headers is None:
        headers = dict()
    if 'User-Agent' not in headers:
        headers[
            'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.24'
    logger.info(f'下载html[{url}][{params}]')
    response = requests.get(url, params, timeout=timeout, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        return response.text
    elif retry > 0:
        return get_html_text(url, params=params, headers=headers, retry=retry - 1, timeout=timeout)


def get_html_tree(url):
    """获取xpath的html_tree, 获取到后可以：html_tree.xpath('//*[@class="test"]')"""
    content = get_html_text(url)
    html_tree = etree.HTML(content)
    return html_tree


def get_m3u8_content(m3u8_url: str, headers: dict[str, str]) -> bytes:
    """获取m3u8内容"""
    response = requests.get(m3u8_url, headers=headers)
    if response.status_code == 200:
        return response.content
