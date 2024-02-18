"""
request请求工具
"""
import re
from typing import Mapping


def is_mobile(user_agent: str) -> bool:
    """判断是否是手机"""
    if user_agent is None:
        return False
    user_agent = user_agent.lower()
    mobile_agent_list = ['ipad', 'iphone os', 'midp', 'rv:1.2.3.4', 'ucweb', 'android', 'windows ce',
                         'windows mobile', 'webview', 'mobile', 'iphone']
    for tmp_mobile_agent in mobile_agent_list:
        if re.search(tmp_mobile_agent, user_agent):
            return True
    return False


def is_json(headers: dict | Mapping) -> bool:
    """是否是json请求"""
    if isinstance(headers, dict) or isinstance(headers, Mapping):
        return headers.get('X-Requested-With') == 'XMLHttpRequest' or (
                headers.get('Accept') and 'application/json' in headers.get('Accept').lower())

