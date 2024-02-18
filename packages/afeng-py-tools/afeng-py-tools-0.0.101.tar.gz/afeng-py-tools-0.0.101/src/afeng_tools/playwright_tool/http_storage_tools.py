"""
playwright工具：pip install pytest-playwright -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
import json
from typing import Any

from playwright.sync_api import Page


def save_storage(page: Page, auth_storage_file):
    """保存storage"""
    # storage['cookies']是 Cookies, storage['origins']是 LocalStorage
    storage = page.context.storage_state(path=auth_storage_file)


def set_storage(page: Page, auth_storage_file):
    """设置storage"""
    page = page.context.browser.new_context(storage_state=auth_storage_file).new_page()
    page.reload()


def get_session_storage(page: Page) -> dict[str, Any]:
    session_storage_str = page.evaluate("() => JSON.stringify(sessionStorage)")
    return json.loads(session_storage_str)


def get_local_storage(page: Page, domain: str) -> dict[str, Any]:
    """获取本地存储空间"""
    storage = page.context.storage_state()
    if storage:
        local_storage = storage['origins']
        for tmp_origin in local_storage:
            if tmp_origin['origin'].startswith(domain):
                storage_dict = {}
                for tmp in tmp_origin['localStorage']:
                    storage_dict[tmp['name']] = tmp['value']
                return storage_dict
