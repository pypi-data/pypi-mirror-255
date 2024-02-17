from pandas import DataFrame

from afeng_tools.tushare_tool.tushare_tools import get_api


def get_stock_list() -> DataFrame:
    """沪深股票-股票列表"""
    ts_api = get_api()
    query_param = {"ts_code": "", "name": "", "exchange": "", "market": "", "is_hs": "", "list_status": "", "limit": "",
                   "offset": ""}
    query_field_list = ["ts_code", "stock_code", "name", "area", "industry", "market", "list_date",
                        "fullname", "enname", "cnspell", "exchange", "curr_type", "list_status",
                        "delist_date", "is_hs", "act_name", "act_ent_type"]
    # 拉取数据
    return ts_api.stock_basic(**query_param, fields=query_field_list)


def get_trade_calendar() -> DataFrame:
    """沪深股票-交易日历"""
    ts_api = get_api()
    query_param = {"exchange": "", "cal_date": "", "start_date": "", "end_date": "", "is_open": "", "limit": "",
                   "offset": ""}
    field_list = ["exchange", "cal_date", "is_open", "pretrade_date"]
    # 拉取数据
    return ts_api.trade_cal(**query_param, fields=field_list)
