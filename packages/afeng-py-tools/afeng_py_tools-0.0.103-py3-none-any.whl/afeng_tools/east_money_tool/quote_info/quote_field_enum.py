import math
from enum import Enum

from afeng_tools.east_money_tool.quote_info.quote_models import QuoteField


class QuoteFieldEnum(Enum):
    """行情字段枚举"""
    quote_code = QuoteField(name='行情代码', fid_list=['f57'], value_func=lambda x: x['f57'])
    quote_name = QuoteField(name='行情名称', fid_list=['f58'], value_func=lambda x: x['f58'])
    quote_full_name = QuoteField(name='行情全名', fid_list=['f734'], value_func=lambda x: x['f734'])
    trade_timestamp = QuoteField(name='交易时间戳', fid_list=['f86'], value_func=lambda x: x['f86'])
    latest_price = QuoteField(name='最新价', fid_list=['f43', 'f59'],
                              value_func=lambda x: round(x['f43'] / (math.pow(10, x['f59'])), x['f59']))
    up_or_down_amount = QuoteField(name='涨跌额', fid_list=['f169', 'f59'],
                                   value_func=lambda x: round(x['f169'] / (math.pow(10, x['f59'])), x['f59']))
    today_begin_price = QuoteField(name='今开', fid_list=['f46', 'f59'],
                                   value_func=lambda x: round(x['f46'] / (math.pow(10, x['f59'])), x['f59']))
    yesterday_end_price = QuoteField(name='昨收', fid_list=['f60', 'f59'],
                                     value_func=lambda x: round(x['f60'] / (math.pow(10, x['f59'])), x['f59']))
    max_price = QuoteField(name='最高价', fid_list=['f44', 'f59'],
                           value_func=lambda x: round(x['f44'] / (math.pow(10, x['f59'])), x['f59']))
    min_price = QuoteField(name='最低价', fid_list=['f45', 'f59'],
                           value_func=lambda x: round(x['f45'] / (math.pow(10, x['f59'])), x['f59']))
    average_price = QuoteField(name='均价', fid_list=['f71', 'f59'],
                               value_func=lambda x: round(x['f71'] / (math.pow(10, x['f59'])), x['f59']))
    max_end_price = QuoteField(name='涨停价', fid_list=['f51', 'f59'],
                               value_func=lambda x: round(x['f51'] / (math.pow(10, x['f59'])), x['f59']))
    min_end_price = QuoteField(name='跌停价', fid_list=['f52', 'f59'],
                               value_func=lambda x: round(x['f52'] / (math.pow(10, x['f59'])), x['f59']))
    quantity_ratio = QuoteField(name='量比', fid_list=['f50', 'f59'],
                                value_func=lambda x: round(x['f50'] / (math.pow(10, x['f59'])), x['f59']))
    transaction_value = QuoteField(name='成交量', fid_list=['f47'], value_func=lambda x: x['f47'])
    transaction_amount = QuoteField(name='成交额', fid_list=['f48'], value_func=lambda x: x['f48'])
    total_share_capital = QuoteField(name='总股本', fid_list=['f84'], value_func=lambda x: x['f84'])
    negotiable_capital = QuoteField(name='流通股本', fid_list=['f85'], value_func=lambda x: x['f85'])
    per_share_value = QuoteField(name='每股净资产', fid_list=['f92'], value_func=lambda x: x['f92'])
    total_market_value = QuoteField(name='总市值', fid_list=['f116'], value_func=lambda x: x['f116'])
    negotiable_market_value = QuoteField(name='流通市值', fid_list=['f117'], value_func=lambda x: x['f117'])
