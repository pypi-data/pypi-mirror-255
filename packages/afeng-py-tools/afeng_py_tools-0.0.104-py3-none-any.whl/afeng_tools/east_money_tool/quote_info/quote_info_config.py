# 行情字段
import math
from datetime import datetime
from typing import Union, Callable

from afeng_tools.east_money_tool.quote_info.quote_models import QuoteItem


def format_number_value(number_value: int, max_width: int = None) -> Union[int, str]:
    """
    控制宽度的格式化数字
    :param number_value:数字值
    :param max_width: 数字宽度
    :return: 格式化后的数字
    """
    if max_width < 0:
        return number_value
    if not number_value:
        return None
    # 后缀
    suffix = ''
    if number_value >= 1000000000000 or number_value <= -1000000000000:
        num = number_value / 1000000000000
        suffix = '万亿'
    elif number_value >= 100000000 or number_value <= -100000000:
        number_value = number_value / 100000000
        suffix = '亿'
    elif number_value >= 10000 or number_value <= -10000:
        number_value = number_value / 10000
        suffix = '万'
    # 整数部分长度
    zs_length = str(number_value).index('.')
    # 如果是负数，整数部分长度减1
    if str(number_value).index('-') == 0:
        zs_length = zs_length - 1
    if zs_length < 0:
        return str(number_value) + suffix

    fixed = max_width - zs_length
    if fixed < 0:
        fixed = 0
    return str(round(number_value, fixed)) + suffix


def formate_quote_item(data_input: Union[str, int], fixed: int = None, color_number: int = None,
                       format_number: int = None, suffix: Union[str, int] = None, to_fixed: int = None) -> QuoteItem:
    """
    转化行情数据为需要的格式
    :param data_input: 输入数据
    :param fixed: 缩小倍数并保留小数位数
    :param color_number: 颜色 大于0红色 小于0 绿色 等于0 灰色 null不设置颜色
    :param format_number: 格式化数据:万、亿、万亿
    :param suffix: 后缀
    :param to_fixed: 保留小数位数
    :return: 转换后的数据
    """
    quote_item = QuoteItem()
    quote_item.source = data_input
    if not data_input or data_input == '-':
        return quote_item
    return_value = data_input
    if isinstance(data_input, int) and fixed and fixed > 0:
        # 缩小倍数并保留小数位数
        if to_fixed and to_fixed > 0:
            return_value = round(data_input / (math.pow(10, fixed)), to_fixed)
        else:
            return_value = round(data_input / (math.pow(10, fixed)), fixed)
    if isinstance(data_input, int) and not fixed and to_fixed and to_fixed > 0:
        # 保留小数位数
        return_value = round(data_input, to_fixed)
    if isinstance(data_input, int) and format_number and format_number > 0:
        # 格式化数据
        return_value = format_number_value(data_input, format_number)
    # 设置文本值
    quote_item.txt = str(return_value) + suffix if suffix else return_value
    # 颜色
    if color_number and color_number > 0:
        quote_item.color = '#f00'
    elif color_number and color_number < 0:
        quote_item.color = '#090'
    # html
    quote_item.html = f'<span style="color:{quote_item.color};">{quote_item.txt}</span>'
    quote_item.blink_html = f'<span>{quote_item.txt}</span>'
    return quote_item


def create_quote_item(fid_list: list,
                      create_quote_item_fun: Callable[[Union[str, int]], QuoteItem]):
    """创建QuoteItem"""
    quote_item = QuoteItem(fid_list)
    quote_item.set_create_fun(create_quote_item_fun)
    return quote_item


def convert_bond_subscription_date(data: dict) -> QuoteItem:
    """
    可转债申购日期
    :param data: 数据
    :return:
    """
    data['f243'] = str(data['f243'])
    color = 0
    if len(data['f243']) >= 8:
        data['f243'] = data['f243'][0:4] + '/' + data['f243'][4:6] + '/' + data['f243'][6:8]
        now_date = datetime.now()
        if now_date.year == data['f243'][0:4] and (now_date.month + 1) == data['f243'][5:7] \
                and now_date.day == data['f243'][8:10]:
            # 如果是今天 标红
            color = 1
    return formate_quote_item(data['f243'], -1, color, -1)


def trans_trade_time(trade_time: int, show_xq: bool = False, show_kh=True) -> str:
    """
    处理交易时间
    :param trade_time: 输入行情时间
    :param show_xq: 是否显示星期
    :param show_kh: 是否显示括号
    :return:
    """
    if not trade_time:
        return '-'
    d = datetime.fromtimestamp(trade_time * 1000)
    week_list = [' 星期日', ' 星期一', ' 星期二', ' 星期三', ' 星期四', ' 星期五', ' 星期六']
    xq = ''
    if show_xq:
        # 星期
        xq = week_list[d.weekday()]
    trade_time_str = str(d.year) + '-' + ("0" + str((d.month + 1)))[0:-2] + '-' \
                     + (("0" + str(d.day))[0:-2]) + xq + ' ' + ("0" + str(d.hour))[0:-2] + ':' \
                     + ("0" + str(d.minute))[0:-2] + ':' + ("0" + str(d.second))[0:-2]
    if show_kh:
        return '（' + trade_time_str + '）'
    return trade_time_str


def deal_trade_state(data_input: int) -> dict:
    """
    处理交易状态
    :param data_input: 输入值
    :return: 返回字典
    """
    state_list = [{
        'txt': '开盘竞价',
        'is_open': True
    }, {
        'txt': '交易中',
        'is_open': True
    }, {
        'txt': '盘中休市',
        'is_open': False
    }, {
        'txt': '收盘竞价',
        'is_open': False
    }, {
        'txt': '已收盘',
        'is_open': False
    }, {
        'txt': '停牌',
        'is_open': False
    }, {
        'txt': '退市',
        'is_open': False
    }, {
        'txt': '暂停上市',
        'is_open': False
    }, {
        'txt': '未上市',
        'is_open': False
    }, {
        'txt': '未开盘',
        'is_open': False
    }, {  # 美股
        'txt': '盘前',
        'is_open': True
    }, {  # 美股
        'txt': '盘后',
        'is_open': True
    }, {
        'txt': '休市',
        'is_open': False
    }, {
        'txt': '盘中停牌',
        'is_open': False
    }, {
        'txt': '非交易代码',
        'is_open': False
    }, {
        'txt': '波动性中断',
        'is_open': False
    }, {  # 沪深
        'txt': '盘后交易启动',
        'is_open': True
    }, {  # 沪深
        'txt': '盘后集中撮合交易',
        'is_open': True
    }, {  # 沪深
        'txt': '盘后固定价格交易',
        'is_open': True
    }]
    return state_list[data_input + 1]


def error_trade_state(data_input: int) -> str:
    """
    异常交易状态
    :param data_input: 输入数据
    :return: 字符串
    """
    trade_state_dict = {
        6: '停牌',
        7: '已退市',
        8: '暂停上市',
        9: '未上市'
    }
    return trade_state_dict[data_input]


def up_or_down_value(data: dict) -> QuoteItem:
    """可转债涨跌额或正股涨跌额"""
    zde = '-'
    if data['f268'] != '-' and data['f267'] != '-':
        zdf = data['f268'] / math.pow(10, data['f152'] + 2)
        zde = (zdf * data['f267']) / (1 + zdf)
    return formate_quote_item(zde, data['f152'], data['f268'], -1)


def deal_date_number(data_input: Union[str, int]) -> QuoteItem:
    """处理行情接口出的数字型日期"""
    if isinstance(data_input, str) and len(data_input) >= 8:
        return QuoteItem().set_source(data_input)
    data_input_str = str(data_input)
    item = QuoteItem()
    item.source = data_input
    item.txt = f'{data_input_str[0:4]}-{data_input_str[4:6]}-{data_input_str[6:8]}'
    return item


def deal_ssrq(ssrq: Union[str, int]) -> Union[str, int]:
    """处理上市日期"""
    if ssrq > 0 and len(str(ssrq)) > 7:
        ssrq = str(ssrq)
        return ssrq[0:4] + '-' + ssrq[4:6] + '-' + ssrq[6:8]
    return ssrq


def deal_cbjd(cbjd: int) -> Union[str, int]:
    """处理财报季度"""
    if cbjd == 1:
        return '一'
    if cbjd == 2:
        return '二'
    if cbjd == 3:
        return '三'
    if cbjd == 4:
        return '四'
    return cbjd


def option_expiration_date(data: dict) -> QuoteItem:
    """期权到期日"""
    show_txt = str(data['f409'])
    if len(show_txt) > 7:
        year = show_txt[0:4]
        this_year = ('000' + str(datetime.now().year))[-4:]
        if year == this_year:
            show_txt = show_txt[4:6] + '-' + show_txt[6:8]
        else:
            show_txt = show_txt[0:4] + '-' + show_txt[4:6] + '-' + show_txt[6:8]
    item = QuoteItem()
    item.txt = show_txt
    item.html = f'<span>{show_txt}</span>'
    item.blink_html = f'<span>{show_txt}</span>'
    item.source = data['f409']
    return item


def key_period_treasury_bond_price_diff(data: dict) -> QuoteItem:
    """关键期国债价差"""
    if not isinstance(data['f19'], int) or not isinstance(data['f39'], int):
        return QuoteItem()
    jc = (data['f19'] - data['f39']) / math.pow(10, data['f59'])
    jc_str = str((jc * 100).toFixed(data['f59'] - 2)) + 'BP'
    return QuoteItem().set_source(jc).set_txt(jc_str).set_html(f'<span>{jc_str}</span>').set_blink_html(f'<span>{jc_str}</span>')


def key_period_treasury_bond_countries(data: dict) -> QuoteItem:
    """关键期国债国家"""
    txt = data['f759']
    if not txt:
        txt = data['f753']
        if not txt:
            txt = '-'
        elif txt == 'US':
            txt = '美国'
        elif txt == 'CN':
            txt = '中国'
        else:
            txt = '-'
    return QuoteItem().set_source(data['f753'] if not data['f759'] else data['f759']).set_txt(txt).set_html(
        f'<span>{txt}</span>').set_blink_html(f'<span>{txt}</span>')


def bond_cj(state: int) -> str:
    """债券-成交方式"""
    state_dict = {
        1: '匹配成交',
        2: '协商成交',
        4: '点击成交',
        8: '意向申报',
        16: '询价成交',
        32: '竞买成交',
        64: '匹配成交大额'
    }
    text = state_dict[state]
    return text if text else '-'

# 列表行情的字段配置
quote_item_config = {
    '名称': QuoteItem(fid_list=['f14']).set_source(lambda x: x['f14']),
    '代码': QuoteItem(fid_list=['f12']).set_source(lambda x: x['f12']),
    '市场': QuoteItem(fid_list=['f13']).set_source(lambda x: x['f13']),
    '行情代码': QuoteItem(fid_list=['f12', 'f13']).set_source(lambda x: x['f13'] + '.' + x['f12']),
    '行情统一链接': QuoteItem(fid_list=['f12', 'f13', 'f14']).set_source(lambda x: (x['f12'], x['f13'], x['f14']))
    .set_txt(lambda x: f'//quote.eastmoney.com/unify/r/{x["f13"]}.{x["f12"]}')
    .set_html(lambda x: f'<a href="//quote.eastmoney.com/unify/r/{x["f13"]}.{x["f12"]}" target="_blank">{x["f14"]}</a>')
    .set_blink_html(
        lambda x: f'<a href="//quote.eastmoney.com/unify/r/{x["f13"]}.{x["f12"]}" target="_blank">{x["f14"]}</a>'),
    '行情统一概念版链接': QuoteItem(fid_list=['f12', 'f13', 'f14']).set_source(lambda x: (x['f12'], x['f13'], x['f14']))
    .set_txt(lambda x: f'//quote.eastmoney.com/unify/cr/{x["f13"]}.{x["f12"]}')
    .set_html(lambda x: f'<a href="//quote.eastmoney.com/unify/cr/{x["f13"]}.{x["f12"]}" target="_blank">{x["f14"]}</a>')
    .set_blink_html(
        lambda x: f'<a href="//quote.eastmoney.com/unify/cr/{x["f13"]}.{x["f12"]}" target="_blank">{x["f14"]}</a>'),
    '最新价': create_quote_item(['f1', 'f2', 'f4'], lambda x: formate_quote_item(x['f2'], x['f1'], x['f4'], -1)),
    '最新价带颜色反转判断': create_quote_item(['f1', 'f2', 'f4', 'f13', 'f19'],
                                              # 关键期国债，颜色反转
                                              lambda x: formate_quote_item(x['f2'], x['f1'], -x['f4'], -1)
                                              if x['f13'] == '171' and x['f19'] in ['1', '2', '4']
                                              else formate_quote_item(x['f2'], x['f1'], x['f4'], -1)),
    '是否颜色反转': create_quote_item(['f13', 'f19'], lambda x: QuoteItem()
                                      .set_txt('true' if x['f13'] == '171' and x['f19'] in ['1', '2', '4'] else 'false')
                                      .source(x['f13'] == '171' and x['f19'] in ['1', '2', '4'])),
    '最新价人民币': create_quote_item(['f251', 'f1', 'f4'],
                                      lambda x: formate_quote_item(x['f251'], x['f1'], x['f4'], -1)),
    '涨跌幅': create_quote_item(['f3', 'f152', 'f4'],
                                lambda x: formate_quote_item(x['f3'], x['f152'], x['f4'], -1, '%')),
    '涨跌幅带颜色反转判断': create_quote_item(['f3', 'f152', 'f4', 'f13', 'f19'],
                                              # 关键期国债，颜色反转
                                              lambda x: formate_quote_item(x['f3'], x['f152'], -x['f4'], -1, '%')
                                              if x['f13'] == '171' and x['f19'] in ['1', '2', '4']
                                              else formate_quote_item(x['f3'], x['f152'], x['f4'], -1, '%')),
    '涨跌幅BP': create_quote_item(['f3', 'f152', 'f4'], lambda x: formate_quote_item(x['f3'], 0, x['f4'], -1)),
    '涨跌幅_5分钟': create_quote_item(['f11', 'f152'],
                                      lambda x: formate_quote_item(x['f11'], x['f152'], x['f11'], -1, '%')),
    '涨跌幅_3日': create_quote_item(['f127', 'f152'],
                                    lambda x: formate_quote_item(x['f127'], x['f152'], x['f127'], -1, '%')),
    '涨跌幅_6日': create_quote_item(['f149', 'f152'],
                                    lambda x: formate_quote_item(x['f149'], x['f152'], x['f149'], -1, '%')),
    '涨跌幅_5日': create_quote_item(['f109', 'f152', 'f4'],
                                    lambda x: formate_quote_item(x['f109'], x['f152'], x['f109'], -1, '%')),
    '涨跌幅_10日': create_quote_item(['f160', 'f152', 'f4'],
                                     lambda x: formate_quote_item(x['f160'], x['f152'], x['f160'], -1, '%')),
    '涨跌额': create_quote_item(['f3', 'f152', 'f4'], lambda x: formate_quote_item(x['f4'], x['f1'], x['f4'], -1)),
    '成交额': create_quote_item(['f6'], lambda x: formate_quote_item(x['f6'], -1, 0, 4)),
    '上涨家数': create_quote_item(['f104'], lambda x: formate_quote_item(x['f104'], -1, 1, -1)),
    '下跌家数': create_quote_item(['f105'], lambda x: formate_quote_item(x['f105'], -1, 1, -1)),
    '平盘家数': create_quote_item(['f106'], lambda x: formate_quote_item(x['f106'], -1, 0, -1)),
    '可转债申购代码': create_quote_item(['f348'], lambda x: formate_quote_item(x['f348'], -1, 0, -1)),
    '可转债申购日期': create_quote_item(['f243'], lambda x: convert_bond_subscription_date(x)),
    '可转债转股溢价率': create_quote_item(['f237', 'f152'],
                                          lambda x: formate_quote_item(x['f237'], x['f152'], x['f237'], -1, '%')),
    '板块领涨股': QuoteItem(fid_list=['f128', 'f140', 'f141']).set_source(lambda x: x['f128']).set_txt(lambda x: x['f128'])
    .set_html(lambda x: f'<a href="//quote.eastmoney.com/unify/r/{x["f141"]}.{x["f140"]}" target="_blank">{x["f128"]}</a>')
    .set_blink_html(
        lambda x: f'<span><a href="//quote.eastmoney.com/unify/r/{x["f141"]}.{x["f140"]}">{x["f128"]}</a></span>'),
    '板块领涨股概念版': QuoteItem(fid_list=['f128', 'f140', 'f141']).set_source(lambda x: x['f128']).set_txt(
        lambda x: x['f128'])
    .set_html(lambda x: f'<a href="//quote.eastmoney.com/unify/cr/{x["f141"]}.{x["f140"]}" target="_blank">{x["f128"]}</a>')
    .set_blink_html(
        lambda x: f'<span><a href="//quote.eastmoney.com/unify/cr/{x["f141"]}.{x["f140"]}">{x["f128"]}</a></span>'),
    '板块领涨股涨跌幅': create_quote_item(['f136'],
                                          lambda x: formate_quote_item(x['f136'], 2, x['f136'], -1, '%')),
    '板块领跌股': QuoteItem(fid_list=['f207', 'f208', 'f209']).set_source(lambda x: x['f207']).set_txt(lambda x: x['f207'])
    .set_html(lambda x: f'<a href="//quote.eastmoney.com/unify/r/{x["f209"]}.{x["f208"]}" target="_blank">{x["f207"]}</a>')
    .set_blink_html(
        lambda x: f'<span><a href="//quote.eastmoney.com/unify/r/{x["f209"]}.{x["f208"]}">{x["f207"]}</a></span>'),
    '板块资金流入最大股': QuoteItem(fid_list=['f204', 'f205', 'f206']).set_source(lambda x: x['f204']).set_txt(
        lambda x: x['f204'])
    .set_html(lambda x: f'<a href="//quote.eastmoney.com/unify/r/{x["f206"]}.{x["f205"]}" target="_blank">{x["f204"]}</a>')
    .set_blink_html(
        lambda x: f'<span><a href="//quote.eastmoney.com/unify/r/{x["f206"]}.{x["f205"]}">{x["f204"]}</a></span>'),
    '主力净额': create_quote_item(['f62'], lambda x: formate_quote_item(x['f62'], -1, x['f62'], 4)),
    '买入价或买一价': create_quote_item(['f31', 'f1'], lambda x: formate_quote_item(x['f31'], x['f1'], 0, -1)),
    '卖出价或卖一价': create_quote_item(['f32', 'f1'], lambda x: formate_quote_item(x['f32'], x['f1'], 0, -1)),
    '交易时间': QuoteItem(fid_list=['f124']).set_source(lambda x: x['f124']).set_txt(lambda x: trans_trade_time(x['f124']))
    .set_html(lambda x: f'<span>{trans_trade_time(x["f124"])}</span>')
    .set_blink_html(lambda x: f'<span>{trans_trade_time(x["f124"])}</span>'),
    '市盈率动态': create_quote_item(['f9', 'f152'], lambda x: formate_quote_item(x['f9'], x['f152'], x['f9'], -1)),
    '总市值': create_quote_item(['f20'], lambda x: formate_quote_item(x['f20'], -1, 0, 4)),
    '净资产': create_quote_item(['f135'], lambda x: formate_quote_item('-' if x['f135'] == 0 else x['f135'], -1, 0, 4)),
    '净利润': create_quote_item(['f45'], lambda x: formate_quote_item(x['f45'], -1, 0, 4)),
    '净利率': create_quote_item(['f129'], lambda x: formate_quote_item(x['f129'], -1, 0, -1, '%', 2)),
    '净利润TTM': create_quote_item(['f138'], lambda x: formate_quote_item(x['f138'], -1, 0, 4)),
    '总营业收入TTM': create_quote_item(['f132'], lambda x: formate_quote_item(x['f132'], -1, 0, 4)),
    '市销率TTM': create_quote_item(['f130'], lambda x: formate_quote_item(x['f130'], -1, 0, -1, None, 2)),
    '市现率TTM': create_quote_item(['f131'], lambda x: formate_quote_item(x['f131'], -1, 0, -1, None, 2)),
    '净资产收益率TTM': create_quote_item(['f137'], lambda x: formate_quote_item(x['f137'], -1, 0, -1, '%', 2)),
    '股息率': create_quote_item(['f133'], lambda x: formate_quote_item(x['f133'], -1, 0, -1, '%', 2)),
    '每股净资产': create_quote_item(['f113'], lambda x: formate_quote_item(x['f113'], -1, 0, 4, None, 2)),
    '市净率': create_quote_item(['f23', 'f152'], lambda x: formate_quote_item(x['f23'], x['f152'], 0, -1)),
    '毛利率': create_quote_item(['f49'], lambda x: formate_quote_item(x['f49'], -1, 0, -1, '%', 2)),
    '主力净流入': create_quote_item(['f62'], lambda x: formate_quote_item(x['f62'], -1, x['f62'], 4)),
    '主力净占比': create_quote_item(['f184', 'f152'],
                                    lambda x: formate_quote_item(x['f184'], x['f152'], x['f184'], -1, '%')),
    '超大单净流入': create_quote_item(['f66'], lambda x: formate_quote_item(x['f66'], -1, x['f66'], 4)),
    '超大单净占比': create_quote_item(['f69', 'f152'],
                                      lambda x: formate_quote_item(x['f69'], x['f152'], x['f69'], -1, '%')),
    '大单净流入': create_quote_item(['f72'], lambda x: formate_quote_item(x['f72'], -1, x['f72'], 4)),
    '大单净占比': create_quote_item(['f75', 'f152'],
                                    lambda x: formate_quote_item(x['f75'], x['f152'], x['f75'], -1, '%')),
    '中单净流入': create_quote_item(['f78'], lambda x: formate_quote_item(x['f78'], -1, x['f78'], 4)),
    '中单净占比': create_quote_item(['f81', 'f152'],
                                    lambda x: formate_quote_item(x['f81'], x['f152'], x['f81'], -1, '%')),
    '小单净流入': create_quote_item(['f84'], lambda x: formate_quote_item(x['f84'], -1, x['f84'], 4)),
    '小单净占比': create_quote_item(['f87', 'f152'],
                                    lambda x: formate_quote_item(x['f87'], x['f152'], x['f87'], -1, '%')),
    '5日主力净额': create_quote_item(['f164'], lambda x: formate_quote_item(x['f164'], -1, x['f164'], 4)),
    '5日主力净占比': create_quote_item(['f165', 'f152'],
                                       lambda x: formate_quote_item(x['f165'], x['f152'], x['f165'], -1, '%')),
    '5日超大单净额': create_quote_item(['f166'], lambda x: formate_quote_item(x['f166'], -1, x['f166'], 4)),
    '5日超大单净占比': create_quote_item(['f167', 'f152'],
                                         lambda x: formate_quote_item(x['f167'], x['f152'], x['f167'], -1, '%')),
    '5日大单净额': create_quote_item(['f168'], lambda x: formate_quote_item(x['f168'], -1, x['f168'], 4)),
    '5日大单净占比': create_quote_item(['f169', 'f152'],
                                       lambda x: formate_quote_item(x['f169'], x['f152'], x['f169'], -1, '%')),
    '5日中单净额': create_quote_item(['f170'], lambda x: formate_quote_item(x['f170'], -1, x['f170'], 4)),
    '5日中单净占比': create_quote_item(['f171', 'f152'],
                                       lambda x: formate_quote_item(x['f171'], x['f152'], x['f171'], -1, '%')),
    '5日小单净额': create_quote_item(['f172'], lambda x: formate_quote_item(x['f172'], -1, x['f172'], 4)),
    '5日小单净占比': create_quote_item(['f173', 'f152'],
                                       lambda x: formate_quote_item(x['f173'], x['f152'], x['f173'], -1, '%')),

    '10日主力净额': create_quote_item(['f174'], lambda x: formate_quote_item(x['f174'], -1, x['f174'], 4)),
    '10日主力净占比': create_quote_item(['f175', 'f152'],
                                        lambda x: formate_quote_item(x['f175'], x['f152'], x['f175'], -1, '%')),
    '10日超大单净额': create_quote_item(['f176'], lambda x: formate_quote_item(x['f176'], -1, x['f176'], 4)),
    '10日超大单净占比': create_quote_item(['f177', 'f152'],
                                          lambda x: formate_quote_item(x['f177'], x['f152'], x['f177'], -1, '%')),
    '10日大单净额': create_quote_item(['f178'], lambda x: formate_quote_item(x['f178'], -1, x['f178'], 4)),
    '10日大单净占比': create_quote_item(['f179', 'f152'],
                                        lambda x: formate_quote_item(x['f179'], x['f152'], x['f179'], -1, '%')),
    '10日中单净额': create_quote_item(['f180'], lambda x: formate_quote_item(x['f180'], -1, x['f180'], 4)),
    '10日中单净占比': create_quote_item(['f181', 'f152'],
                                        lambda x: formate_quote_item(x['f181'], x['f152'], x['f181'], -1, '%')),
    '10日小单净额': create_quote_item(['f182'], lambda x: formate_quote_item(x['f182'], -1, x['f182'], 4)),
    '10日小单净占比': create_quote_item(['f183', 'f152'],
                                        lambda x: formate_quote_item(x['f183'], x['f152'], x['f183'], -1, '%')),

    'AB股对应的代码': QuoteItem(fid_list=['f201']).set_source(lambda x: x['f201']).set_txt(lambda x: x['f201'])
    .set_html(lambda x: f'<span>{x["f201"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f201"]}</span>'),
    'AB股对应的名称': QuoteItem(fid_list=['f203']).set_source(lambda x: x['f203']).set_txt(lambda x: x['f203'])
    .set_html(lambda x: f'<span>{x["f203"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f203"]}</span>'),
    'AB股对应的市场': QuoteItem(fid_list=['f202']).set_source(lambda x: x['f202']).set_txt(lambda x: x['f202'])
    .set_html(lambda x: f'<span>{x["f202"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f202"]}</span>'),
    'AB股对应的最新价': create_quote_item(['f196', 'f200', 'f197'],
                                          lambda x: formate_quote_item(x['f196'], x['f200'], x['f197'], -1)),
    'AB股对应的涨跌幅': create_quote_item(['f197', 'f152'],
                                          lambda x: formate_quote_item(x['f197'], x['f152'], x['f197'], -1, '%')),
    'AB股比价': create_quote_item(['f199', 'f152'], lambda x: formate_quote_item(x['f199'], x['f152'], 0, -1)),
    '成交量': create_quote_item(['f5'], lambda x: formate_quote_item(x['f5'], -1, 0, 4)),
    '最高价': create_quote_item(['f15', 'f1', 'f18'],
                                lambda x: formate_quote_item(x['f15'], x['f1'], x['f15'], -x['f18'], -1)),
    '最低价': create_quote_item(['f16', 'f1', 'f18'],
                                lambda x: formate_quote_item(x['f16'], x['f1'], x['f16'], -x['f18'], -1)),
    '换手率': create_quote_item(['f8', 'f152'],
                                lambda x: formate_quote_item(x['f8'], x['f152'], 0, -1, '%')),
    '市盈率TTM': create_quote_item(['f9', 'f152'],
                                   lambda x: formate_quote_item(x['f9'], x['f152'], 0, -1)),
    '股东权益': create_quote_item(['f58'],
                                  lambda x: formate_quote_item(x['f58'], -1, 0, 4)),
    '行业板块的成分股数': create_quote_item(['f134'],
                                            lambda x: formate_quote_item(x['f134'], -1, 0, -1)),
    '总市值行业排名': create_quote_item(['f1020'],
                                        lambda x: formate_quote_item(x['f1020'], -1, 0, -1)),
    '净资产行业排名': create_quote_item(['f1135'],
                                        lambda x: formate_quote_item(x['f1135'], -1, 0, -1)),
    '净利润行业排名': create_quote_item(['f1045'],
                                        lambda x: formate_quote_item(x['f1045'], -1, 0, -1)),
    '净利润TTM行业排名': create_quote_item(['f1138'],
                                           lambda x: formate_quote_item(x['f1138'], -1, 0, -1)),
    '市盈率动态行业排名': create_quote_item(['f1009'],
                                            lambda x: formate_quote_item(x['f1009'], -1, 0, -1)),
    '市盈率TTM行业排名': create_quote_item(['f1115'],
                                           lambda x: formate_quote_item(x['f1115'], -1, 0, -1)),
    '市净率行业排名': create_quote_item(['f1023'],
                                        lambda x: formate_quote_item(x['f1023'], -1, 0, -1)),
    '毛利率行业排名': create_quote_item(['f1049'],
                                        lambda x: formate_quote_item(x['f1049'], -1, 0, -1)),
    '净利率行业排名': create_quote_item(['f1129'],
                                        lambda x: formate_quote_item(x['f1129'], -1, 0, -1)),
    'ROE行业排名': create_quote_item(['f1037'],
                                     lambda x: formate_quote_item(x['f1037'], -1, 0, -1)),
    'ROETTM行业排名': create_quote_item(['f1137'],
                                        lambda x: formate_quote_item(x['f1137'], -1, 0, -1)),
    '股东权益行业排名': create_quote_item(['f1058'],
                                          lambda x: formate_quote_item(x['f1058'], -1, 0, -1)),
    '总营业收入TTM行业排名': create_quote_item(['f1132'],
                                               lambda x: formate_quote_item(x['f1132'], -1, 0, -1)),
    '市销率TTM行业排名': create_quote_item(['f1130'],
                                           lambda x: formate_quote_item(x['f1130'], -1, 0, -1)),
    '市现率TTM行业排名': create_quote_item(['f1131'],
                                           lambda x: formate_quote_item(x['f1131'], -1, 0, -1)),
    '股息率行业排名': create_quote_item(['f1133'],
                                        lambda x: formate_quote_item(x['f1133'], -1, 0, -1)),
    '总市值行业排名四分位': create_quote_item(['f3020'],
                                              lambda x: formate_quote_item(x['f3020'], -1, 0, -1)),
    '净资产行业排名四分位': create_quote_item(['f3135'],
                                              lambda x: formate_quote_item(x['f3135'], -1, 0, -1)),
    '净利润行业排名四分位': create_quote_item(['f3045'],
                                              lambda x: formate_quote_item(x['f3045'], -1, 0, -1)),
    '净利润TTM行业排名四分位': create_quote_item(['f3138'],
                                                 lambda x: formate_quote_item(x['f3138'], -1, 0, -1)),
    '市盈率动态行业排名四分位': create_quote_item(['f3009'],
                                                  lambda x: formate_quote_item(x['f3009'], -1, 0, -1)),
    '市盈率TTM行业排名四分位': create_quote_item(['f3115'],
                                                 lambda x: formate_quote_item(x['f3115'], -1, 0, -1)),
    '市净率行业排名四分位': create_quote_item(['f3023'],
                                              lambda x: formate_quote_item(x['f3023'], -1, 0, -1)),
    '毛利率行业排名四分位': create_quote_item(['f3049'],
                                              lambda x: formate_quote_item(x['f3049'], -1, 0, -1)),
    '净利率行业排名四分位': create_quote_item(['f3129'],
                                              lambda x: formate_quote_item(x['f3129'], -1, 0, -1)),
    'ROE行业排名四分位': create_quote_item(['f3037'],
                                           lambda x: formate_quote_item(x['f3037'], -1, 0, -1)),
    'ROETTM行业排名四分位': create_quote_item(['f3137'],
                                              lambda x: formate_quote_item(x['f3137'], -1, 0, -1)),
    '股东权益行业排名四分位': create_quote_item(['f3058'],
                                                lambda x: formate_quote_item(x['f3058'], -1, 0, -1)),
    '总营业收入TTM行业排名四分位': create_quote_item(['f3132'],
                                                     lambda x: formate_quote_item(x['f3132'], -1, 0, -1)),
    '市销率TTM行业排名四分位': create_quote_item(['f3130'],
                                                 lambda x: formate_quote_item(x['f3130'], -1, 0, -1)),
    '市现率TTM行业排名四分位': create_quote_item(['f3131'],
                                                 lambda x: formate_quote_item(x['f3131'], -1, 0, -1)),
    '股息率行业排名四分位': create_quote_item(['f3133'],
                                              lambda x: formate_quote_item(x['f3133'], -1, 0, -1)),
    '期权行权价': create_quote_item(['f161', 'f330'],
                                    lambda x: formate_quote_item(x['f161'], x['f330'], 0, -1)),
    '今持仓': create_quote_item(['f108'],
                                lambda x: formate_quote_item(x['f108'], -1, 0, 4)),
    '期权隐含波动率': create_quote_item(['f249', 'f152'],
                                        lambda x: formate_quote_item(x['f249'], x['f152'], 0, -1, '%')),
    '期权折溢价率': create_quote_item(['f250', 'f152'],
                                      lambda x: formate_quote_item(x['f250'], x['f152'], 0, -1, '%')),
    '量比': create_quote_item(['f10', 'f152'],
                              lambda x: formate_quote_item(x['f10'], x['f152'], 0, -1)),
    '净资产收益率ROE': create_quote_item(['f37'],
                                         lambda x: formate_quote_item(x['f37'], -1, 0, -1, '%', 2)),
    '总市值行业平均': create_quote_item(['f2020'],
                                        lambda x: formate_quote_item(x['f2020'], -1, 0, 4)),
    '净资产行业平均': create_quote_item(['f2135'],
                                        lambda x: formate_quote_item(x['f2135'], -1, 0, 4)),
    '净利润行业平均': create_quote_item(['f2045'],
                                        lambda x: formate_quote_item(x['f2045'], -1, 0, 4)),
    '市盈率动态行业平均': create_quote_item(['f2009'],
                                            lambda x: formate_quote_item(x['f2009'], -1, 0, 4)),
    '市净率行业平均': create_quote_item(['f2023'],
                                        lambda x: formate_quote_item(x['f2023'], -1, 0, 4)),
    '毛利率行业平均': create_quote_item(['f2049'],
                                        lambda x: formate_quote_item(x['f2049'], -1, 0, -1, '%', 2)),
    '净利率行业平均': create_quote_item(['f2129'],
                                        lambda x: formate_quote_item(x['f2129'], -1, 0, -1, '%', 2)),
    'ROE行业平均': create_quote_item(['f2037'],
                                     lambda x: formate_quote_item(x['f2037'], -1, 0, -1, '%', 2)),
    '二级分类': QuoteItem(fid_list=['f19']).set_source(lambda x: x['f19']).set_txt(lambda x: x['f19'])
    .set_html(lambda x: f'<span>{x["f19"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f19"]}</span>'),
}

one_item_config = {

    '买十价': create_quote_item(['f1', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f1'], x['f59'], x['f1'] - x['f60'], -1)),
    '买十量': create_quote_item(['f2'], lambda x: formate_quote_item(x['f2'], -1, 0, 4)),
    '买九价': create_quote_item(['f3', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f3'], x['f59'], x['f3'] - x['f60'], -1)),
    '买九量': create_quote_item(['f4'], lambda x: formate_quote_item(x['f4'], -1, 0, 4)),
    '买八价': create_quote_item(['f5', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f5'], x['f59'], x['f5'] - x['f60'], -1)),
    '买八量': create_quote_item(['f6'], lambda x: formate_quote_item(x['f6'], -1, 0, 4)),
    '买七价': create_quote_item(['f7', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f7'], x['f59'], x['f7'] - x['f60'], -1)),
    '买七量': create_quote_item(['f8'], lambda x: formate_quote_item(x['f8'], -1, 0, 4)),
    '买六价': create_quote_item(['f9', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f9'], x['f59'], x['f9'] - x['f60'], -1)),
    '买六量': create_quote_item(['f10'], lambda x: formate_quote_item(x['f10'], -1, 0, 4)),

    '买五价': create_quote_item(['f11', 'f59', 'f60', 'f531'],
                                lambda x: formate_quote_item(x['f11'], x['f59'], x['f11'] - x['f60'], -1)),
    '买五量': create_quote_item(['f12', 'f531'],
                                lambda x: formate_quote_item(x['f12'], -1, 0, 4)),
    '买四价': create_quote_item(['f13', 'f59', 'f60', 'f531'],
                                lambda x: formate_quote_item(x['f13'], x['f59'], x['f13'] - x['f60'], -1)),
    '买四量': create_quote_item(['f14', 'f531'],
                                lambda x: formate_quote_item(x['f14'], -1, 0, 4)),
    '买三价': create_quote_item(['f15', 'f59', 'f60', 'f531'],
                                lambda x: formate_quote_item(x['f15'], x['f59'], x['f15'] - x['f60'], -1)),
    '买三量': create_quote_item(['f16', 'f531'],
                                lambda x: formate_quote_item(x['f16'], -1, 0, 4)),
    '买二价': create_quote_item(['f17', 'f59', 'f60', 'f531'],
                                lambda x: formate_quote_item(x['f17'], x['f59'], x['f17'] - x['f60'], -1)),
    '买二量': create_quote_item(['f18', 'f531'],
                                lambda x: formate_quote_item(x['f18'], -1, 0, 4)),
    '买入价或买一价': create_quote_item(['f19', 'f59', 'f60', 'f532'],
                                        lambda x: formate_quote_item(x['f19'], x['f59'], x['f19'] - x['f60'], -1)),
    '买一量': create_quote_item(['f20', 'f532'],
                                lambda x: formate_quote_item(x['f20'], -1, 0, 4)),

    '卖十价': create_quote_item(['f21', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f21'], x['f59'], x['f21'] - x['f60'], -1)),
    '卖十量': create_quote_item(['f22'], lambda x: formate_quote_item(x['f22'], -1, 0, 4)),
    '卖九价': create_quote_item(['f23', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f23'], x['f59'], x['f21'] - x['f60'], -1)),
    '卖九量': create_quote_item(['f24'], lambda x: formate_quote_item(x['f24'], -1, 0, 4)),
    '卖八价': create_quote_item(['f25', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f25'], x['f59'], x['f25'] - x['f60'], -1)),
    '卖八量': create_quote_item(['f26'], lambda x: formate_quote_item(x['f26'], -1, 0, 4)),
    '卖七价': create_quote_item(['f27', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f27'], x['f59'], x['f27'] - x['f60'], -1)),
    '卖七量': create_quote_item(['f28'], lambda x: formate_quote_item(x['f28'], -1, 0, 4)),
    '卖六价': create_quote_item(['f29', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f29'], x['f59'], x['f29'] - x['f60'], -1)),
    '卖六量': create_quote_item(['f30'], lambda x: formate_quote_item(x['f30'], -1, 0, 4)),
    '卖五价': create_quote_item(['f31', 'f59', 'f60', 'f531'],
                                lambda x: formate_quote_item(x['f31'], x['f59'], x['f31'] - x['f60'], -1)),
    '卖五量': create_quote_item(['f32', 'f531'],
                                lambda x: formate_quote_item(x['f32'], -1, 0, 4)),
    '卖四价': create_quote_item(['f33', 'f59', 'f60', 'f531'],
                                lambda x: formate_quote_item(x['f33'], x['f59'], x['f33'] - x['f60'], -1)),
    '卖四量': create_quote_item(['f34', 'f531'],
                                lambda x: formate_quote_item(x['f34'], -1, 0, 4)),
    '卖三价': create_quote_item(['f35', 'f59', 'f60', 'f531'],
                                lambda x: formate_quote_item(x['f35'], x['f59'], x['f35'] - x['f60'], -1)),
    '卖三量': create_quote_item(['f36', 'f531'],
                                lambda x: formate_quote_item(x['f36'], -1, 0, 4)),
    '卖二价': create_quote_item(['f37', 'f59', 'f60', 'f531'],
                                lambda x: formate_quote_item(x['f37'], x['f59'], x['f37'] - x['f60'], -1)),
    '卖二量': create_quote_item(['f38', 'f531'],
                                lambda x: formate_quote_item(x['f38'], -1, 0, 4)),
    '卖出价或卖一价': create_quote_item(['f39', 'f59', 'f60', 'f532'],
                                        lambda x: formate_quote_item(x['f39'], x['f59'], x['f39'] - x['f60'], -1)),
    '卖一量': create_quote_item(['f40', 'f532'],
                                lambda x: formate_quote_item(x['f40'], -1, 0, 4)),
    '最新价': create_quote_item(['f43', 'f59', 'f169'],
                                lambda x: formate_quote_item(x['f43'], x['f59'], x['f169'], -1)),
    '最高价': create_quote_item(['f44', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f44'], x['f59'], x['f44'] - x['f60'], -1)),
    '股票期权最高价': create_quote_item(['f44', 'f59', 'f130'],
                                        lambda x: formate_quote_item(x['f44'], x['f59'], x['f44'] - x['f130'], -1)),
    '最低价': create_quote_item(['f45', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f45'], x['f59'], x['f45'] - x['f60'], -1)),
    '股票期权最低价': create_quote_item(['f45', 'f59', 'f130'],
                                        lambda x: formate_quote_item(x['f45'], x['f59'], x['f45'] - x['f130'], -1)),
    '今开': create_quote_item(['f46', 'f59', 'f60'],
                              lambda x: formate_quote_item(x['f46'], x['f59'], x['f46'] - x['f60'], -1)),
    '股票期权今开': create_quote_item(['f46', 'f59', 'f130'],
                                      lambda x: formate_quote_item(x['f46'], x['f59'], x['f46'] - x['f130'], -1)),
    '成交量': create_quote_item(['f47'],
                                lambda x: formate_quote_item(x['f47'], -1, 0, 4)),
    '成交量带手': create_quote_item(['f47'],
                                    lambda x: formate_quote_item(x['f47'], -1, 0, 4, '手')),
    '成交额': create_quote_item(['f48'],
                                lambda x: formate_quote_item(x['f48'], -1, 0, 4)),
    '外盘': create_quote_item(['f49'], lambda x: formate_quote_item(x['f49'], -1, -1, 4)),
    '量比': create_quote_item(['f50', 'f152'], lambda x: formate_quote_item(x['f50'], x['f152'], 0, -1)),
    '涨停价': create_quote_item(['f51', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f51'], x['f59'], x['f51'] - x['f60'], -1)),
    '跌停价': create_quote_item(['f52', 'f59', 'f60'],
                                lambda x: formate_quote_item(x['f52'], x['f59'], x['f52'] - x['f60'], -1)),
    '每股收益': create_quote_item(['f55'], lambda x: formate_quote_item(x['f55'], -1, 0, 4)),
    '代码': QuoteItem(fid_list=['f57']).set_source(lambda x: x['f57']).set_txt(lambda x: x['f57'])
    .set_html(lambda x: f'<span>{x["f57"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f57"]}</span>'),
    '行情代码': QuoteItem(fid_list=['f57', 'f107']).set_source(lambda x: x['f57'] + '.' + x['f107'])
    .set_txt(lambda x: x['f57'] + '.' + x['f107'])
    .set_html(lambda x: f'<span>{x["f57"] + "." + x["f107"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f57"] + "." + x["f107"]}</span>'),
    '行情统一链接': QuoteItem(fid_list=['f57', 'f58', 'f107']).set_source(lambda x: x['f57'] + '.' + x['f107'])
    .set_txt(lambda x: f'//quote.eastmoney.com/unify/r/{x["f107"]}.{x["f57"]}')
    .set_html(lambda x: f'<a href="//quote.eastmoney.com/unify/r/{x["f107"]}.{x["f57"]}" target="_blank">{x["f58"]}</a>')
    .set_blink_html(lambda x: f'<a href="//quote.eastmoney.com/unify/r/{x["f107"]}.{x["f57"]}">{x["f58"]}</a>'),
    '行情统一概念版链接': QuoteItem(fid_list=['f57', 'f58', 'f107']).set_source(lambda x: x['f57'] + '.' + x['f107'])
    .set_txt(lambda x: f'//quote.eastmoney.com/unify/cr/{x["f107"]}.{x["f57"]}')
    .set_html(lambda x: f'<a href="//quote.eastmoney.com/unify/cr/{x["f107"]}.{x["f57"]}" target="_blank">{x["f58"]}</a>')
    .set_blink_html(lambda x: f'<a href="//quote.eastmoney.com/unify/cr/{x["f107"]}.{x["f57"]}">{x["f58"]}</a>'),
    '名称': QuoteItem(fid_list=['f58']).set_source(lambda x: x['f58']).set_txt(lambda x: x['f58'])
    .set_html(lambda x: f'<span>{x["f58"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f58"]}</span>'),
    '关键期国债价差': create_quote_item(['f19', 'f39', 'f59'],
                                        lambda x: key_period_treasury_bond_price_diff(x)),
    '昨收': create_quote_item(['f60', 'f59'],
                              lambda x: formate_quote_item(x['f60'], x['f59'], 0, -1)),
    '财报季度': QuoteItem(fid_list=['f62']).set_source(lambda x: x['f62'])
    .set_txt(lambda x: deal_cbjd(x['f62']))
    .set_html(lambda x: f'<span>{deal_cbjd(x["f62"])}</span>')
    .set_blink_html(lambda x: f'<span>{deal_cbjd(x["f62"])}</span>'),

    '均价': create_quote_item(['f71', 'f59', 'f60'],
                              lambda x: formate_quote_item(x['f71'], x['f59'], x['f71'] - x['f60'], -1)),
    '股票期权均价': create_quote_item(['f71', 'f59', 'f130'],
                                      lambda x: formate_quote_item(x['f71'], x['f59'], x['f71'] - x['f130'], -1)),
    '债券加权平均': create_quote_item(['f71', 'f59'],
                                      lambda x: formate_quote_item(x['f71'], x['f59'], 0, -1)),

    '总股本': create_quote_item(['f84'], lambda x: formate_quote_item(x['f84'], -1, 0, 4)),
    '流通股本': create_quote_item(['f85'], lambda x: formate_quote_item(x['f85'], -1, 0, 4)),
    '交易时间': QuoteItem(fid_list=['f86']).set_source(lambda x: x['f86'])
    .set_txt(lambda x: trans_trade_time(x['f86']))
    .set_html(lambda x: f'<span>{trans_trade_time(x["f86"])}</span>')
    .set_blink_html(lambda x: f'<span>{trans_trade_time(x["f86"])}</span>'),
    '交易时间不带括号': QuoteItem(fid_list=['f86']).set_source(lambda x: x['f86'])
    .set_txt(lambda x: trans_trade_time(x['f86'], False, False))
    .set_html(lambda x: f'<span>{trans_trade_time(x["f86"], False, False)}</span>')
    .set_blink_html(lambda x: f'<span>{trans_trade_time(x["f86"], False, False)}</span>'),
    '交易时间带星期': QuoteItem(fid_list=['f86']).set_source(lambda x: x['f86'])
    .set_txt(lambda x: trans_trade_time(x['f86'], True))
    .set_html(lambda x: f'<span>{trans_trade_time(x["f86"], True)}</span>')
    .set_blink_html(lambda x: f'<span>{trans_trade_time(x["f86"], True)}</span>'),

    '每股净资产': create_quote_item(['f92', 'f59'], lambda x: formate_quote_item(x['f92'], -1, 0, -1, None, x['f59'])),
    '净利润': create_quote_item(['f105'], lambda x: formate_quote_item(x['f105'], -1, 0, 4)),
    '市场': QuoteItem(fid_list=['f107']).set_source(lambda x: x['f107']).set_txt(lambda x: x['f107'])
    .set_html(lambda x: f'<span>{x["f107"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f107"]}</span>'),
    '每股收益TTM': create_quote_item(['f108'], lambda x: formate_quote_item(x['f108'], -1, 0, 4, None, 2)),

    '二级分类': QuoteItem(fid_list=['f111']).set_source(lambda x: x['f111'])
    .set_txt(lambda x: x['f111'])
    .set_html(lambda x: f'<span>{x["f111"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f111"]}</span>'),
    'JYS': QuoteItem(fid_list=['f112']).set_source(lambda x: x['f112']).set_txt(lambda x: x['f112'])
    .set_html(lambda x: f'<span>{x["f112"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f112"]}</span>'),
    '上涨家数': create_quote_item(['f113'], lambda x: formate_quote_item(x['f113'], -1, 1, -1)),
    '下跌家数': create_quote_item(['f114'], lambda x: formate_quote_item(x['f114'], -1, -1, -1)),
    '平盘家数': create_quote_item(['f115'], lambda x: formate_quote_item(x['f115'], -1, 0, -1)),
    '总市值': create_quote_item(['f116'], lambda x: formate_quote_item(x['f116'], -1, 0, 4)),
    '总市值_短': create_quote_item(['f116'], lambda x: formate_quote_item(x['f116'], -1, 0, 2)),
    '流通市值': create_quote_item(['f117'], lambda x: formate_quote_item(x['f117'], -1, 0, 4)),
    '流通市值_短': create_quote_item(['f117'], lambda x: formate_quote_item(x['f117'], -1, 0, 2)),

    '涨跌幅_5日': create_quote_item(['f119', 'f152'],
                                    lambda x: formate_quote_item(x['f119'], x['f152'], x['f119'], -1, '%')),

    '涨跌幅_20日': create_quote_item(['f120', 'f152'],
                                     lambda x: formate_quote_item(x['f120'], x['f152'], x['f120'], -1, '%')),
    '涨跌幅_60日': create_quote_item(['f121', 'f152'],
                                     lambda x: formate_quote_item(x['f121'], x['f152'], x['f121'], -1, '%')),
    '涨跌幅_今年以来': create_quote_item(['f122', 'f152'],
                                         lambda x: formate_quote_item(x['f122'], x['f152'], x['f122'], -1, '%')),
    '相对大盘指数1月涨跌幅': create_quote_item(['f123', 'f152'],
                                               lambda x: formate_quote_item(x['f123'], x['f152'], 0, -1, '%')),
    '相对大盘指数3月涨跌幅': create_quote_item(['f124', 'f152'],
                                               lambda x: formate_quote_item(x['f124'], x['f152'], 0, -1, '%')),
    '相对大盘指数52周涨跌幅': create_quote_item(['f125', 'f152'],
                                                lambda x: formate_quote_item(x['f125'], x['f152'], 0, -1, '%')),
    '股息率': create_quote_item(['f126'], lambda x: formate_quote_item(x['f126'], -1, 0, -1, '%')),

    '昨结算': create_quote_item(['f130', 'f59'], lambda x: formate_quote_item(x['f130'], x['f59'], 0, -1)),
    '今结算': create_quote_item(['f131', 'f59'], lambda x: formate_quote_item(x['f131'], x['f59'], 0, -1)),
    '昨持仓': create_quote_item(['f132'], lambda x: formate_quote_item(x['f132'], -1, 0, 4)),
    '今持仓': create_quote_item(['f133'], lambda x: formate_quote_item(x['f133'], -1, 0, 4)),
    '仓差': create_quote_item(['f134'], lambda x: formate_quote_item(x['f134'], -1, 0, 4)),
    '主力流入': create_quote_item(['f135'], lambda x: formate_quote_item(x['f135'], -1, 1, 4)),
    '主力流出': create_quote_item(['f136'], lambda x: formate_quote_item(x['f136'], -1, -1, 4)),
    '主力净流入': create_quote_item(['f137'], lambda x: formate_quote_item(x['f137'], -1, x['f137'], 4)),
    '超大单流入': create_quote_item(['f138'], lambda x: formate_quote_item(x['f138'], -1, 1, 4)),
    '超大单流出': create_quote_item(['f139'], lambda x: formate_quote_item(x['f139'], -1, -1, 4)),
    '超大单净流入': create_quote_item(['f140'], lambda x: formate_quote_item(x['f140'], -1, x['f140'], 4)),
    '大单流入': create_quote_item(['f141'], lambda x: formate_quote_item(x['f141'], -1, 1, 4)),
    '大单流出': create_quote_item(['f142'], lambda x: formate_quote_item(x['f142'], -1, -1, 4)),
    '大单净流入': create_quote_item(['f143'], lambda x: formate_quote_item(x['f143'], -1, x['f143'], 4)),
    '中单流入': create_quote_item(['f144'], lambda x: formate_quote_item(x['f144'], -1, 1, 4)),
    '中单流出': create_quote_item(['f145'], lambda x: formate_quote_item(x['f145'], -1, -1, 4)),
    '中单净流入': create_quote_item(['f146'], lambda x: formate_quote_item(x['f146'], -1, x['f146'], 4)),
    '小单流入': create_quote_item(['f147'], lambda x: formate_quote_item(x['f147'], -1, 1, 4)),
    '小单流出': create_quote_item(['f148'], lambda x: formate_quote_item(x['f148'], -1, -1, 4)),
    '小单净流入': create_quote_item(['f149'], lambda x: formate_quote_item(x['f149'], -1, x['f149'], 4)),

    '内盘': create_quote_item(['f161'], lambda x: formate_quote_item(x['f161'], -1, -1, 4)),
    '市盈率动态': create_quote_item(['f162', 'f152'], lambda x: formate_quote_item(x['f162'], x['f152'], 0, -1)),
    '市盈率静态': create_quote_item(['f163', 'f152'], lambda x: formate_quote_item(x['f163'], x['f152'], 0, -1)),
    '市盈率TTM': create_quote_item(['f164', 'f152'], lambda x: formate_quote_item(x['f164'], x['f152'], 0, -1)),
    '市净率': create_quote_item(['f167', 'f152'], lambda x: formate_quote_item(x['f167'], x['f152'], 0, -1)),
    '换手率': create_quote_item(['f168', 'f152'], lambda x: formate_quote_item(x['f168'], x['f152'], 0, -1, '%')),
    '质押式回购债券涨跌BP': create_quote_item(['f169', 'f59'],
                                              lambda x: formate_quote_item(x['f169'] * 100 if isinstance(x['f169'], int)
                                                                           else x['f169'], x['f59'], 0, -1, None, 2)),
    '涨跌额': create_quote_item(['f169', 'f59'],
                                lambda x: formate_quote_item(x['f169'], x['f59'], x['f169'], -1)),
    '涨跌幅': create_quote_item(['f170', 'f152', 'f169'],
                                lambda x: formate_quote_item(x['f170'], x['f152'], x['f169'], -1, '%')),
    '振幅': create_quote_item(['f171', 'f152'], lambda x: formate_quote_item(x['f171'], x['f152'], 0, -1, '%')),
    '净资产收益率ROE': create_quote_item(['f173'], lambda x: formate_quote_item(x['f173'], -1, 0, -1, '%', 2)),
    '52周最高价': create_quote_item(['f174', 'f59', 'f59', 'f60'],
                                    lambda x: formate_quote_item(x['f174'], x['f59'], x['f174'] - x['f60'], -1)),
    '52周最低价': create_quote_item(['f175', 'f59', 'f59', 'f60'],
                                    lambda x: formate_quote_item(x['f175'], x['f59'], x['f175'] - x['f60'], -1)),

    '股票标识': QuoteItem(fid_list=['f177']).set_source(lambda x: x['f177'])
    .set_txt(lambda x: x['f177'])
    .set_html(lambda x: f'<span>{x["f177"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f177"]}</span>'),

    '扩展类型': create_quote_item(['f182'],
                                  lambda x: formate_quote_item(x['f182'], -1, 0, -1)),
    '营业总收入': create_quote_item(['f183'], lambda x: formate_quote_item(x['f183'], -1, 0, 4)),
    '营业总收入同比': create_quote_item(['f184'], lambda x: formate_quote_item(x['f184'], -1, 0, -1, '%', 2)),
    '净利润同比': create_quote_item(['f185'], lambda x: formate_quote_item(x['f185'], -1, 0, -1, '%', 2)),
    '毛利率': create_quote_item(['f186'], lambda x: formate_quote_item(x['f186'], -1, 0, -1, '%', 2)),
    '净利率': create_quote_item(['f187'], lambda x: formate_quote_item(x['f187'], -1, 0, -1, '%', 2)),
    '资产负债率': create_quote_item(['f188'], lambda x: formate_quote_item(x['f188'], -1, 0, -1, '%', 2)),
    '上市日期': QuoteItem(fid_list=['f189']).set_source(lambda x: x['f189'])
    .set_txt(lambda x: deal_ssrq(x['f189']))
    .set_html(lambda x: f'<span>{deal_ssrq(x["f189"])}</span>')
    .set_blink_html(lambda x: f'<span>{deal_ssrq(x["f189"])}</span>'),
    '每股未分配利润': create_quote_item(['f190'], lambda x: formate_quote_item(x['f190'], -1, 0, 4)),

    '委比': create_quote_item(['f191', 'f152'], lambda x: formate_quote_item(x['f191'], x['f152'], x['f191'], -1, '%')),
    '委差': create_quote_item(['f192'], lambda x: formate_quote_item(x['f192'], -1, x['f192'], 4)),
    '主力净占比': create_quote_item(['f193', 'f152'],
                                    lambda x: formate_quote_item(x['f193'], x['f152'], x['f193'], -1, '%')),
    '超大单净占比': create_quote_item(['f194', 'f152'],
                                      lambda x: formate_quote_item(x['f194'], x['f152'], x['f194'], -1, '%')),
    '大单净占比': create_quote_item(['f195', 'f152'],
                                    lambda x: formate_quote_item(x['f195'], x['f152'], x['f195'], -1, '%')),
    '中单净占比': create_quote_item(['f196', 'f152'],
                                    lambda x: formate_quote_item(x['f196'], x['f152'], x['f196'], -1, '%')),
    '小单净占比': create_quote_item(['f197', 'f152'],
                                    lambda x: formate_quote_item(x['f197'], x['f152'], x['f197'], -1, '%')),

    '所属行业板块代码': QuoteItem(fid_list=['f198']).set_source(lambda x: x['f198'])
    .set_txt(lambda x: x['f198'])
    .set_html(lambda x: f'<span>{x["f198"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f198"]}</span>'),
    '所属行业板块市场': QuoteItem(fid_list=['f199']).set_source(lambda x: x['f199'])
    .set_txt(lambda x: x['f199'])
    .set_html(lambda x: f'<span>{x["f199"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f199"]}</span>'),

    '卖五差量': create_quote_item(['f206'],
                                  lambda x: formate_quote_item('', -1, None, 4)
                                  if x['f206'] == '-' or x['f206'] == 0 or x['f206'] is None
                                  else formate_quote_item(x['f206'], -1, x['f206'], 4)),
    '卖四差量': create_quote_item(['f207'],
                                  lambda x: formate_quote_item('', -1, None, 4)
                                  if x['f207'] == '-' or x['f207'] == 0 or x['f207'] is None
                                  else formate_quote_item(x['f207'], -1, x['f207'], 4)),
    '卖三差量': create_quote_item(['f208'],
                                  lambda x: formate_quote_item('', -1, None, 4)
                                  if x['f208'] == '-' or x['f208'] == 0 or x['f208'] is None
                                  else formate_quote_item(x['f208'], -1, x['f208'], 4)),
    '卖二差量': create_quote_item(['f209'],
                                  lambda x: formate_quote_item('', -1, None, 4)
                                  if x['f209'] == '-' or x['f209'] == 0 or x['f209'] is None
                                  else formate_quote_item(x['f209'], -1, x['f209'], 4)),
    '卖一差量': create_quote_item(['f210'],
                                  lambda x: formate_quote_item('', -1, None, 4)
                                  if x['f210'] == '-' or x['f210'] == 0 or x['f210'] is None
                                  else formate_quote_item(x['f210'], -1, x['f210'], 4)),
    '买一差量': create_quote_item(['f211'],
                                  lambda x: formate_quote_item('', -1, None, 4)
                                  if x['f211'] == '-' or x['f211'] == 0 or x['f211'] is None
                                  else formate_quote_item(x['f211'], -1, x['f211'], 4)),
    '买二差量': create_quote_item(['f212'],
                                  lambda x: formate_quote_item('', -1, None, 4)
                                  if x['f212'] == '-' or x['f212'] == 0 or x['f212'] is None
                                  else formate_quote_item(x['f212'], -1, x['f212'], 4)),
    '买三差量': create_quote_item(['f213'],
                                  lambda x: formate_quote_item('', -1, None, 4)
                                  if x['f213'] == '-' or x['f213'] == 0 or x['f213'] is None
                                  else formate_quote_item(x['f213'], -1, x['f213'], 4)),
    '买四差量': create_quote_item(['f214'],
                                  lambda x: formate_quote_item('', -1, None, 4)
                                  if x['f214'] == '-' or x['f214'] == 0 or x['f214'] is None
                                  else formate_quote_item(x['f214'], -1, x['f214'], 4)),
    '买五差量': create_quote_item(['f215'],
                                  lambda x: formate_quote_item('', -1, None, 4)
                                  if x['f215'] == '-' or x['f215'] == 0 or x['f215'] is None
                                  else formate_quote_item(x['f215'], -1, x['f215'], 4)),

    '卖十席位数': create_quote_item(['f221'], lambda x: formate_quote_item(x['f221'], -1, 0, 4)),
    '卖九席位数': create_quote_item(['f222'], lambda x: formate_quote_item(x['f222'], -1, 0, 4)),
    '卖八席位数': create_quote_item(['f223'], lambda x: formate_quote_item(x['f223'], -1, 0, 4)),
    '卖七席位数': create_quote_item(['f224'], lambda x: formate_quote_item(x['f224'], -1, 0, 4)),
    '卖六席位数': create_quote_item(['f225'], lambda x: formate_quote_item(x['f225'], -1, 0, 4)),
    '卖五席位数': create_quote_item(['f226'], lambda x: formate_quote_item(x['f226'], -1, 0, 4)),
    '卖四席位数': create_quote_item(['f227'], lambda x: formate_quote_item(x['f227'], -1, 0, 4)),
    '卖三席位数': create_quote_item(['f228'], lambda x: formate_quote_item(x['f228'], -1, 0, 4)),
    '卖二席位数': create_quote_item(['f229'], lambda x: formate_quote_item(x['f229'], -1, 0, 4)),
    '卖一席位数': create_quote_item(['f230'], lambda x: formate_quote_item(x['f230'], -1, 0, 4)),

    '买一席位数': create_quote_item(['f231'], lambda x: formate_quote_item(x['f231'], -1, 0, 4)),
    '买二席位数': create_quote_item(['f232'], lambda x: formate_quote_item(x['f232'], -1, 0, 4)),
    '买三席位数': create_quote_item(['f233'], lambda x: formate_quote_item(x['f233'], -1, 0, 4)),
    '买四席位数': create_quote_item(['f234'], lambda x: formate_quote_item(x['f234'], -1, 0, 4)),
    '买五席位数': create_quote_item(['f235'], lambda x: formate_quote_item(x['f235'], -1, 0, 4)),
    '买六席位数': create_quote_item(['f236'], lambda x: formate_quote_item(x['f236'], -1, 0, 4)),
    '买七席位数': create_quote_item(['f237'], lambda x: formate_quote_item(x['f237'], -1, 0, 4)),
    '买八席位数': create_quote_item(['f238'], lambda x: formate_quote_item(x['f238'], -1, 0, 4)),
    '买九席位数': create_quote_item(['f239'], lambda x: formate_quote_item(x['f239'], -1, 0, 4)),
    '买十席位数': create_quote_item(['f240'], lambda x: formate_quote_item(x['f240'], -1, 0, 4)),

    'AH股对应的最新价': create_quote_item(['f251', 'f255', 'f252'],
                                          lambda x: formate_quote_item(x['f251'], x['f255'], x['f252'], -1)),
    'AH股对应的涨跌幅': create_quote_item(['f252', 'f152'],
                                          lambda x: formate_quote_item(x['f252'], x['f152'], x['f252'], -1, '%')),
    'AH股对应的溢价率': create_quote_item(['f253', 'f152'],
                                          lambda x: formate_quote_item(x['f253'], x['f152'], x['f253'], -1, '%')),
    'AH股对应的比价': create_quote_item(['f254', 'f152'], lambda x: formate_quote_item(x['f254'], x['f152'], 0, -1)),

    'AH股对应的代码': QuoteItem(fid_list=['f256']).set_source(lambda x: x['f256'])
    .set_txt(lambda x: x['f256'])
    .set_html(lambda x: f'<span>{x["f256"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f256"]}</span>'),
    'AH股对应的市场': QuoteItem(fid_list=['f257']).set_source(lambda x: x['f257'])
    .set_txt(lambda x: x['f257'])
    .set_html(lambda x: f'<span>{x["f257"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f257"]}</span>'),
    'AH股对应的名称': QuoteItem(fid_list=['f258']).set_source(lambda x: x['f258'])
    .set_txt(lambda x: x['f258'])
    .set_html(lambda x: f'<span>{x["f258"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f258"]}</span>'),

    '盘后成交量': create_quote_item(['f260'],
                                    lambda x: formate_quote_item(x['f260'], -1, 0, 4)),
    '盘后成交额': create_quote_item(['f261'],
                                    lambda x: formate_quote_item(x['f261'], -1, 0, 4)),

    '可转债代码或正股代码': create_quote_item(['f262'], lambda x: formate_quote_item(x['f262'], -1, 0, -1)),
    '可转债市场或正股市场': create_quote_item(['f263'], lambda x: formate_quote_item(x['f263'], -1, 0, -1)),
    '可转债名称或正股名称': create_quote_item(['f264'], lambda x: formate_quote_item(x['f264'], -1, 0, -1)),
    '可转债最新价或正股最新价': create_quote_item(['f267', 'f265', 'f268'],
                                                  lambda x: formate_quote_item(x['f267'], x['f265'], x['f268'], -1)),
    '可转债涨跌额或正股涨跌额': create_quote_item(['f267', 'f268', 'f152'], lambda x: up_or_down_value(x)),
    '可转债涨跌幅或正股涨跌幅': create_quote_item(['f268', 'f152'],
                                                  lambda x: formate_quote_item(x['f268'], x['f152'], x['f268'], -1,
                                                                               '%')),

    'AB股对应的代码': QuoteItem(fid_list=['f269']).set_source(lambda x: x['f269'])
    .set_txt(lambda x: x['f269'])
    .set_html(lambda x: f'<span>{x["f269"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f269"]}</span>'),
    'AB股对应的市场': QuoteItem(fid_list=['f270']).set_source(lambda x: x['f270'])
    .set_txt(lambda x: x['f270'])
    .set_html(lambda x: f'<span>{x["f270"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f270"]}</span>'),
    'AB股对应的名称': QuoteItem(fid_list=['f271']).set_source(lambda x: x['f271'])
    .set_txt(lambda x: x['f271'])
    .set_html(lambda x: f'<span>{x["f271"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f271"]}</span>'),
    'AB股比价': create_quote_item(['f276', 'f152'], lambda x: formate_quote_item(x['f276'], x['f152'], 0, -1)),
    '注册股本': create_quote_item(['f277'], lambda x: formate_quote_item(x['f277'], -1, 0, 4)),
    '发行股本': create_quote_item(['f278'], lambda x: formate_quote_item(x['f278'], -1, 0, 4)),
    '是否同股同权': QuoteItem(fid_list=['f279']).set_source(lambda x: x['f279'])
    .set_txt(lambda x: '是' if x['f279'] == 1 else '否')
    .set_html(lambda x: f'<span>{"是" if x["f279"] == 1 else "否"}</span>')
    .set_blink_html(lambda x: f'<span>{"是" if x["f279"] == 1 else "否"}</span>'),
    '是否表决权差异': QuoteItem(fid_list=['f279']).set_source(lambda x: x['f279'])
    .set_txt(lambda x: '是' if x['f279'] == 1 else '否')
    .set_html(lambda x: f'<span>{"是" if x["f279"] == 1 else "否"}</span>')
    .set_blink_html(lambda x: f'<span>{"是" if x["f279"] == 1 else "否"}</span>'),

    'A股对应GDR或GDR对应A股的代码': QuoteItem(fid_list=['f285']).set_source(lambda x: x['f285'])
    .set_txt(lambda x: x['f285'])
    .set_html(lambda x: f'<span>{x["f285"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f285"]}</span>'),
    'A股对应GDR或GDR对应A股的市场': QuoteItem(fid_list=['f286']).set_source(lambda x: x['f286'])
    .set_txt(lambda x: x['f286'])
    .set_html(lambda x: f'<span>{x["f286"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f286"]}</span>'),
    'A股对应GDR或GDR对应A股的名称': QuoteItem(fid_list=['f287']).set_source(lambda x: x['f287'])
    .set_txt(lambda x: x['f287'])
    .set_html(lambda x: f'<span>{x["f287"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f287"]}</span>'),

    '是否尚未盈利': QuoteItem(fid_list=['f288']).set_source(lambda x: x['f288'])
    .set_txt(lambda x: '是' if x['f288'] == 1 else '否')
    .set_html(lambda x: f'<span>{"是" if x["f288"] == 1 else "否"}</span>')
    .set_blink_html(lambda x: f'<span>{"是" if x["f288"] == 1 else "否"}</span>'),

    '是否盈利': QuoteItem(fid_list=['f288']).set_source(lambda x: x['f288'])
    .set_txt(lambda x: '是' if x['f288'] == 0 else '否')
    .set_html(lambda x: f'<span>{"是" if x["f288"] == 0 else "否"}</span>')
    .set_blink_html(lambda x: f'<span>{"是" if x["f288"] == 0 else "否"}</span>'),

    '涨跌幅_10日': create_quote_item(['f291', 'f152'],
                                     lambda x: formate_quote_item(x['f291'], x['f152'], x['f291'], -1, '%')),
    '交易状态': QuoteItem(fid_list=['f292']).set_source(lambda x: deal_trade_state(x['f292']))
    .set_txt(lambda x: deal_trade_state(x['f292'])['txt'])
    .set_html(lambda x: f'<span>{deal_trade_state(x["f292"])["txt"]}</span>')
    .set_blink_html(lambda x: f'<span>{deal_trade_state(x["f292"])["txt"]}</span>')
    .set_color(lambda x: '#f00' if deal_trade_state(x["f292"])["is_open"] else '#090'),
    '异常交易状态': QuoteItem(fid_list=['f292']).set_source(lambda x: error_trade_state(x['f292']))
    .set_txt(lambda x: error_trade_state(x['f292']))
    .set_html(lambda x: f'<span>{error_trade_state(x["f292"])}</span>')
    .set_blink_html(lambda x: f'<span>{error_trade_state(x["f292"])}</span>')
    .set_color(lambda x: '#f00' if error_trade_state(x["f292"]) else '#090'),

    '是否注册制': QuoteItem(fid_list=['f294']).set_source(lambda x: x['f294'])
    .set_txt(lambda x: '是' if x['f294'] == 1 else '否')
    .set_html(lambda x: f'<span>{"是" if x["f294"] == 1 else "否"}</span>')
    .set_blink_html(lambda x: f'<span>{"是" if x["f294"] == 1 else "否"}</span>'),
    '是否具有协议控制架构': QuoteItem(fid_list=['f295']).set_source(lambda x: x['f295'])
    .set_txt(lambda x: '是' if x['f295'] == 1 else '否')
    .set_html(lambda x: f'<span>{"是" if x["f295"] == 1 else "否"}</span>')
    .set_blink_html(lambda x: f'<span>{"是" if x["f295"] == 1 else "否"}</span>'),

    '成交笔数': create_quote_item(['f296'], lambda x: formate_quote_item(x['f296'], -1, 0, 4)),
    '最后价格': create_quote_item(['f301', 'f60', 'f59'],
                                  lambda x: formate_quote_item(x['f301'] if x['f301'] != 0 else x['f60'], x['f59'], 0,
                                                               -1)),

    '期权购沽对应的最新价': create_quote_item(['f401', 'f403', 'f402'],
                                              lambda x: formate_quote_item(x['f401'], x['f403'], x['f402'], -1)),
    '期权购沽对应的涨跌幅': create_quote_item(['f402', 'f152'],
                                              lambda x: formate_quote_item(x['f402'], x['f152'], x['f402'], -1, '%')),

    '期权购沽对应的代码': create_quote_item(['f404'], lambda x: formate_quote_item(x['f404'], -1, 0, -1)),
    '期权购沽对应的市场': create_quote_item(['f405'], lambda x: formate_quote_item(x['f405'], -1, 0, -1)),
    '期权购沽对应的证券名称': create_quote_item(['f406'], lambda x: formate_quote_item(x['f406'], -1, 0, -1)),
    '期权剩余日期': create_quote_item(['f407'], lambda x: formate_quote_item(x['f407'], -1, 0, -1)),
    '期权合约单位': create_quote_item(['f408'], lambda x: formate_quote_item(x['f408'], -1, 0, -1)),
    '期权到期日': create_quote_item(['f409'], lambda x: option_expiration_date(x)),
    '期权行权价': create_quote_item(['f410', 'f481'], lambda x: formate_quote_item(x['f410'], x['f481'], 0, -1)),
    '期权内在价值': create_quote_item(['f411', 'f59'], lambda x: formate_quote_item(x['f411'], x['f59'], 0, -1)),
    '期权隐含波动率': create_quote_item(['f412', 'f152'],
                                        lambda x: formate_quote_item(x['f412'], x['f152'], 0, -1, '%')),
    '期权折溢价率': create_quote_item(['f413', 'f152'], lambda x: formate_quote_item(x['f413'], x['f152'], 0, -1, '%')),
    '期权Delta': create_quote_item(['f414', 'f154'],
                                   lambda x: formate_quote_item(x['f414'], x['f154'], 0, -1)),
    '期权Gamma': create_quote_item(['f415', 'f154'],
                                   lambda x: formate_quote_item(x['f415'], x['f154'], 0, -1)),
    '期权Vega': create_quote_item(['f416', 'f154'],
                                  lambda x: formate_quote_item(x['f416'], x['f154'], 0, -1)),
    '期权Theta': create_quote_item(['f417', 'f154'],
                                   lambda x: formate_quote_item(x['f417'], x['f154'], 0, -1)),
    '期权Rho': create_quote_item(['f418', 'f154'],
                                 lambda x: formate_quote_item(x['f418'], x['f154'], 0, -1)),
    '30日波动率': create_quote_item(['f419', 'f154'],
                                    lambda x: formate_quote_item(x['f419'], x['f154'], 0, -1, '%')),
    '60日波动率': create_quote_item(['f420', 'f154'],
                                    lambda x: formate_quote_item(x['f420'], x['f154'], 0, -1, '%')),
    '120日波动率': create_quote_item(['f421', 'f154'],
                                     lambda x: formate_quote_item(x['f421'], x['f154'], 0, -1, '%')),
    '240日波动率': create_quote_item(['f422', 'f154'],
                                     lambda x: formate_quote_item(x['f422'], x['f154'], 0, -1, '%')),
    '纯债价值': create_quote_item(['f424', 'f154'],
                                  lambda x: formate_quote_item(x['f424'], x['f154'], 0, -1)),

    '可转债申购日期': create_quote_item(['f425'], lambda x: formate_quote_item(x['f425'], -1, 0, -1)),
    '可转债转股价': create_quote_item(['f426', 'f265'], lambda x: formate_quote_item(x['f426'], x['f265'], 0, -1)),
    '可转债转股价值': create_quote_item(['f427', 'f154'], lambda x: formate_quote_item(x['f427'], x['f154'], 0, -1)),
    '可转债转股溢价率': create_quote_item(['f428', 'f152'],
                                          lambda x: formate_quote_item(x['f428'], x['f152'], x['f428'], -1, '%')),
    '可转债回售触发价': create_quote_item(['f430', 'f265'],
                                          lambda x: formate_quote_item(x['f430'], x['f265'], 0, -1)),
    '可转债强赎触发价': create_quote_item(['f431', 'f265'],
                                          lambda x: formate_quote_item(x['f431'], x['f265'], 0, -1)),
    '可转债到期赎回价': create_quote_item(['f432', 'f265'],
                                          lambda x: formate_quote_item(x['f432'], x['f265'], 0, -1)),
    '可转债转股日期': create_quote_item(['f433'], lambda x: deal_date_number(x['f433'])),

    '现手': create_quote_item(['f452'], lambda x: formate_quote_item(abs(x['f452']), -1, x['f452'], 4) if x[
        'f452'] else formate_quote_item('-', -1, 0, 4)),
    '可转债申购代码': create_quote_item(['f478'], lambda x: formate_quote_item(x['f478'], -1, 0, -1)),

    '交易币种': QuoteItem(fid_list=['f600']).set_source(lambda x: x['f600'])
    .set_txt(lambda x: x['f600'])
    .set_html(lambda x: f'<span>{x["f600"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f600"]}</span>'),
    '交易币种_汇率': create_quote_item(['f601', 'f154'], lambda x: formate_quote_item(x['f601'], x['f154'], 0, -1)),

    '债券最新匹配成交价': create_quote_item(['f700', 'f59', 'f60'],
                                            lambda x: formate_quote_item(x['f700'], x['f59'], x['f700'] - x['f60'],
                                                                         -1)),
    '债券当日匹配成交量': create_quote_item(['f701'],
                                            lambda x: formate_quote_item(x['f701'], -1, 0, 4)),
    '债券当日匹配成交额': create_quote_item(['f702'],
                                            lambda x: formate_quote_item(x['f702'], -1, 0, 4)),
    '债券最新YTM': create_quote_item(['f703', 'f154'],
                                     lambda x: formate_quote_item(x['f703'], x['f154'], 0, -1, '%', 2)),
    '债券涨跌BP': create_quote_item(['f704', 'f152'],
                                    lambda x: formate_quote_item(x['f704'] / 100 if isinstance(x['f704'], int)
                                                                 else x['f704'], x['f152'], 0, -1)),
    '债券加权平均涨跌BP': create_quote_item(['f705', 'f152'],
                                            lambda x: formate_quote_item(x['f705'], x['f152'], 0, -1)),
    '债券最近成交方式': create_quote_item(['f706'],
                                          lambda x: formate_quote_item(bond_cj(x['f706']), -1, 0, -1)),

    '债券昨加权平均': create_quote_item(['f721', 'f59'],
                                        lambda x: formate_quote_item(x['f721'], x['f59'], 0, -1)),

    '扩位简称': QuoteItem(fid_list=['f734']).set_source(lambda x: x['f734']).set_txt(lambda x: x['f734'])
    .set_html(lambda x: f'<span>{x["f734"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f734"]}</span>'),

    '做市商数': QuoteItem(fid_list=['f740']).set_source(lambda x: x['f740'])
    .set_txt(lambda x: x['f740'])
    .set_html(lambda x: f'<span>{x["f740"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f740"]}</span>'),

    'A瑞士对应的最新价': create_quote_item(['f743', 'f746', 'f744'],
                                           lambda x: formate_quote_item(x['f743'], x['f746'], x['f744'], -1)),
    'A瑞士对应的涨跌幅': create_quote_item(['f744', 'f152'],
                                           lambda x: formate_quote_item(x['f744'], x['f152'], x['f744'], -1, '%')),
    'A瑞士溢价率': create_quote_item(['f745', 'f152'], lambda x: formate_quote_item(x['f745'], x['f152'], 0, -1)),
    'A瑞士对应的代码': QuoteItem(fid_list=['f747']).set_source(lambda x: x['f747'])
    .set_txt(lambda x: x['f747'])
    .set_html(lambda x: f'<span>{x["f747"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f747"]}</span>'),
    'A瑞士对应的市场': QuoteItem(fid_list=['f748']).set_source(lambda x: x['f748'])
    .set_txt(lambda x: x['f748'])
    .set_html(lambda x: f'<span>{x["f748"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f748"]}</span>'),
    'A瑞士对应的名称': QuoteItem(fid_list=['f749']).set_source(lambda x: x['f749'])
    .set_txt(lambda x: x['f749'])
    .set_html(lambda x: f'<span>{x["f749"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f749"]}</span>'),
    'A瑞士比价': create_quote_item(['f750', 'f152'], lambda x: formate_quote_item(x['f750'], x['f152'], 0, -1)),
    '港股对应人民币计价或者反过来对应的代码': QuoteItem(fid_list=['f751']).set_source(lambda x: x['f751'])
    .set_txt(lambda x: x['f751'])
    .set_html(lambda x: f'<span>{x["f751"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f751"]}</span>'),

    '港股对应人民币计价或者反过来对应的市场': QuoteItem(fid_list=['f752']).set_source(lambda x: x['f752'])
    .set_txt(lambda x: x['f752'])
    .set_html(lambda x: f'<span>{x["f752"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f752"]}</span>'),

    '关键期国债国家': create_quote_item(['f753', 'f759'], lambda x: key_period_treasury_bond_countries(x)),
    '关键期国债期限': QuoteItem(fid_list=['f754']).set_source(lambda x: x['f754']).set_txt(lambda x: x['f754'])
    .set_html(lambda x: f'<span>{x["f754"]}</span>')
    .set_blink_html(lambda x: f'<span>{x["f754"]}</span>'),
}
# TODO
