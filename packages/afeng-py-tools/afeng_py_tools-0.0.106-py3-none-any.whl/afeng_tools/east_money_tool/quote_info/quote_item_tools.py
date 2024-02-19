"""
东方财富行情QuoteItem工具类
"""
from afeng_tools.east_money_tool.quote_info.quote_info_config import one_item_config
from afeng_tools.east_money_tool.quote_info.quote_models import QuoteItem


def one_item_fields(item_list: list[QuoteItem]):
    fids = []
    for tmp in item_list:
        fids.extend(tmp.fid_list)
    fids = filter(lambda x: x != 'f531' and x != 'f532', fids)
    return ','.join(fids)


if __name__ == '__main__':
    item_fields = ['名称','扩位简称','市场','代码','行情代码','最新价','最后价格','涨跌幅','涨跌额','股票标识','二级分类','行情统一链接','今开','昨收','最高价','最低价','成交量','盘后成交量','成交量带手','成交额','盘后成交额','是否同股同权','是否表决权差异','注册股本','发行股本','是否盈利','买入价或买一价','买二价','买三价','买四价','买五价','买一量','买二量','买三量','买四量','买五量',
'卖出价或卖一价','卖二价','卖三价','卖四价','卖五价','卖一量','卖二量','卖三量','卖四量','卖五量','买一差量','买二差量','买三差量','买四差量','买五差量',
'卖一差量','卖二差量','卖三差量','卖四差量','卖五差量','内盘','外盘','振幅','量比','交易时间带星期','总股本','流通股本','换手率','每股收益TTM','总市值','市净率','市盈率TTM','市盈率动态','市盈率静态','每股净资产','均价','流通市值','流通市值_短','交易状态','涨停价','跌停价','总市值','委比','委差','异常交易状态','可转债代码或正股代码','是否注册制','是否具有协议控制架构','AB股对应的代码','AB股对应的市场','AH股对应的代码','AH股对应的市场','A股对应GDR或GDR对应A股的代码','A股对应GDR或GDR对应A股的市场','A瑞士对应的市场','A瑞士对应的代码']
    item_list = []
    for tmp_field in item_fields:
        item_list.append(one_item_config[tmp_field])
    fids = one_item_fields(item_list)
    print(fids)
