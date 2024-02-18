"""
playwright工具：pip install pytest-playwright -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import time
from typing import Callable

from playwright.sync_api import Page, sync_playwright

from afeng_tools.playwright_tool import http_header_tools, http_cookie_tools
from afeng_tools.playwright_tool.decorator.playwright_decorators import auto_input


@auto_input(headless=True)
def refresh_cookie_and_header_file(refresh_url: str, cookie_file: str, header_file: str, web_page: Page = None,
                                   sleep_seconds: int = 1) -> None:
    """
    刷新cookie和header文件
    :param refresh_url: 属性数据的请求的url
    :param cookie_file: cookie文件路径
    :param header_file: header文件路径
    :param web_page: 自动注入的Page
    :param sleep_seconds: 为避免高频请求睡眠的秒数
    :return: None
    """
    http_header_tools.save_headers(web_page, header_file)
    print('*' * 10, refresh_url)
    web_page.goto(refresh_url)
    # 为避免高频请求导致网站封ip，需要睡眠一会，小于等于0则不会睡眠
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)
    http_cookie_tools.save_cookies(web_page, cookie_file)


def run_page_work(headless: bool, work_func: Callable):
    """
    执行页面工作
    :param headless: 是否有请求头
    :param work_func: 执行工作的函数，必须要有参数:web_page:Page
    :return:
    """
    with sync_playwright() as pw:
        browser_args = ['--start-maximized']
        browser = pw.chromium.launch(headless=headless, timeout=1000 * 60 * 10, args=browser_args)
        page = browser.new_page(no_viewport=True)
        try:
            if isinstance(work_func, Callable):
                return work_func(web_page=page)
            else:
                return work_func.__func__(web_page=page)
        finally:
            if page:
                page.close()
            browser.close()


