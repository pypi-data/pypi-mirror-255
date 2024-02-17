"""
东方财富Http请求工具类
"""
import json
import os.path
import re
from pathlib import Path

import requests

from afeng_tools.datetime_tool.datetime_tools import get_timestamp
from afeng_tools.east_money_tool.config.web_url_config import get_url
from afeng_tools.file_tool.tmp_file_tools import get_user_tmp_dir
from afeng_tools.http_tool.decorator.http_auto_retry_tools import auto_retry
from afeng_tools.math_tool import random_tools
from afeng_tools.playwright_tool.http_cookie_tools import get_cookies
from afeng_tools.playwright_tool.http_header_tools import get_headers
from afeng_tools.playwright_tool.playwright_tools import refresh_cookie_and_header_file

WORK_PATH = get_user_tmp_dir()

def load_auth_file(cookie_file_name, header_file_name, refresh_url) -> tuple:
    save_path = os.path.join(WORK_PATH, 'auth-file')
    os.makedirs(save_path, exist_ok=True)
    cookie_file = os.path.join(save_path, cookie_file_name)
    header_file = os.path.join(save_path, header_file_name)
    if not os.path.exists(cookie_file) or not os.path.exists(header_file):
        refresh_cookie_and_header_file(refresh_url=refresh_url,
                                       cookie_file=cookie_file, header_file=header_file)
    return cookie_file, header_file


@auto_retry(retry_count=3)
def get_datacenter_data(stock_code: str, opt_dict: dict, cookie_file: str, header_file: str):
    url = 'https:' + get_url('datacenter') + 'api/data/v1/get'
    params = {
        'callback': f'jQuery{random_tools.random_number_str(length=21)}_{get_timestamp()}',
        'filter': "(SECURITY_CODE=\"" + stock_code + "\")",
        'columns': 'ALL',
        'source': 'WEB',
        'client': 'WEB',
    }
    params.update(opt_dict)
    file_path = Path(__file__).parent
    cookies = get_cookies(os.path.join(file_path, cookie_file))
    headers = get_headers(os.path.join(file_path, header_file))
    response = requests.get(url=url, params=params, cookies=cookies, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        response_text = response.text
        re_match = re.match(f'^{params["callback"]}\((.*)\);', response_text)
        if re_match:
            json_str = re_match.group(1)
            return json.loads(json_str)


@auto_retry(retry_count=3)
def http_get(data_url: str, params: dict, cookie_file: str, header_file: str, jsonp: bool = False):
    jsonp_field = 'callback'
    if jsonp:
        if 'cb' in params:
            jsonp_field = 'cb'
        params[jsonp_field] = f'jQuery{random_tools.random_number_str(length=21)}_{get_timestamp()}'
    file_path = Path(__file__).parent
    cookies = get_cookies(os.path.join(file_path, cookie_file))
    headers = get_headers(os.path.join(file_path, header_file))
    response = requests.get(url=data_url, params=params, cookies=cookies, headers=headers)
    if response.status_code == 200:
        response.encoding = 'utf-8'
        response_text = response.text
        if jsonp:
            re_match = re.match(f'^{params[jsonp_field]}\((.*)\);', response_text)
            if re_match:
                json_str = re_match.group(1)
                return json.loads(json_str)
        else:
            return json.loads(response_text)

if __name__ == '__main__':
    pass
