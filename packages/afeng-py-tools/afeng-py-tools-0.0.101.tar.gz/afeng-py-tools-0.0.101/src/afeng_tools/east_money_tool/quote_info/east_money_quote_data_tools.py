"""
东方财富获取行情工具类
"""
from afeng_tools.datetime_tool import datetime_tools
from afeng_tools.east_money_tool.config.web_url_config import get_url
from afeng_tools.east_money_tool.tool.east_money_http_tools import http_get


def get_one_quote(quote_code: str, item_list: list[str]):
    """
    获取单个的行情数据
    :param quote_code: 行情代码
    :param item_list: 配置列表
    :return:
    """
    ut = None
    data_url = get_url('quote_api') + 'api/qt/stock/get?invt=2&fltt=1'
    param = http_get(data_url=data_url, params={
        'cb': '?',
        'fields':'',
        'secid':'',
        'ut':ut,
        'wbp2u': 'delayparams',
        '_':datetime_tools.get_timestamp()
    }, cookie_file='', header_file='', jsonp=True)

    def get_one_quote_sse():
        pass
