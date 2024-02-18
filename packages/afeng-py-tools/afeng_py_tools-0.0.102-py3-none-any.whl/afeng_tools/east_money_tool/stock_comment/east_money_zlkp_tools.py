"""
页面：https://data.eastmoney.com/stockcomment/stock/688981.html
主力控盘
"""
from afeng_tools.east_money_tool.tool.east_money_http_tools import get_datacenter_data
from afeng_tools.east_money_tool.tool.east_money_load_auth_tools import load_stock_comment_auth_file


def load_jgcy(stock_code: str, page_size: int = 22):
    """加载机构参与程度-折线图数据"""
    cookie_file, header_file = load_stock_comment_auth_file(stock_code)
    response_data = get_datacenter_data(stock_code=stock_code,
                                        opt_dict={'reportName': 'RPT_DMSK_TS_STOCKEVALUATE',
                                       'sortColumns': "TRADE_DATE",
                                       'sortTypes': "-1",
                                       'pageSize': page_size
                                       },
                                        cookie_file=cookie_file,
                                        header_file=header_file)
    if response_data['success'] and response_data['result']:
        result = response_data['result']
        total_count = result['count']
        # total_pages = result['pages']
        # if total_count > page_size:
        #     return load_jgcy(stock_code=stock_code, page_size=total_count)
        return result['data']


if __name__ == '__main__':
    load_jgcy(stock_code='000001')
