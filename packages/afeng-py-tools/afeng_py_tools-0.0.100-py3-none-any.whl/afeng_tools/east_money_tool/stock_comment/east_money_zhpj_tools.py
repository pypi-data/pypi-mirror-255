"""
东方财富综合评价模块
"""
from afeng_tools.east_money_tool.tool.east_money_http_tools import get_datacenter_data
from afeng_tools.east_money_tool.tool.east_money_load_auth_tools import load_stock_comment_auth_file


def load_zf_pm(stock_code):
    cookie_file, header_file = load_stock_comment_auth_file(stock_code)
    json_data = get_datacenter_data(stock_code='001268',
                                    opt_dict={'reportName': 'RPT_CUSTOM_STOCK_PK'},
                                    cookie_file=cookie_file,
                                    header_file=header_file)
    print(json_data)
def load_zdyc():
    """涨跌预测"""
    pass

def load_lspf():
    pass

def load_zhpm():
    pass