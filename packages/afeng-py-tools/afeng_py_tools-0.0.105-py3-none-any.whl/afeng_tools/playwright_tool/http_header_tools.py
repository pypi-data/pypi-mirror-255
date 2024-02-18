"""
playwright工具：pip install pytest-playwright -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""

import json

from playwright.sync_api import Page


def _save_request_headers(auth_header_file: str):
    def wrap_call(req):
        all_headers_dict = req.all_headers()
        user_headers = dict()
        user_headers["cookie"] = all_headers_dict.get("cookie")
        user_headers['Host'] = all_headers_dict.get('Host')
        user_headers["referer"] = all_headers_dict.get("referer")
        user_headers["user-agent"] = all_headers_dict.get("user-agent")
        user_headers["authorization"] = all_headers_dict.get("authorization")
        user_headers["origin"] = all_headers_dict.get("origin")
        header_str = json.dumps(user_headers)
        with open(auth_header_file, 'wb') as header_file:
            header_file.write(header_str.encode('utf-8'))
    return wrap_call


def save_headers(page: Page, auth_header_file):
    """保存header"""
    page.on("requestfinished", _save_request_headers(auth_header_file))

def set_headers(page: Page, auth_header_file):
    """设置header"""
    with open(auth_header_file, 'rb') as header_file:
        header_str = header_file.read()
    header_dict = json.loads(header_str)
    page.set_extra_http_headers(header_dict)
    page.reload()

def get_headers(auth_header_file) -> dict:
    """获取header"""
    with open(auth_header_file, 'rb') as header_file:
        header_str = header_file.read()
        return json.loads(header_str)
