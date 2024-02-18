"""
东方财富加载认证的工具类
"""
from afeng_tools.east_money_tool.tool.east_money_http_tools import load_auth_file


def load_stock_comment_auth_file(stock_code: str) -> tuple:
    """
    加载综合评价页面的认证文件: https://data.eastmoney.com/stockcomment/stock/688981.html
    :param stock_code: 股票代码
    :return: 返回结果：cookie_file, header_file
    """
    return load_auth_file(cookie_file_name=f'eastmoney_stock_comment_{stock_code}_cookie.txt',
                          header_file_name=f'eastmoney_stock_comment_{stock_code}_header.txt',
                          refresh_url=f'https://data.eastmoney.com/stockcomment/stock/{stock_code}.html')
