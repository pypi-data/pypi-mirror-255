"""
pip install tushare
"""
import tushare


def get_api(tushare_token: str):
    """获取API"""
    return tushare.pro_api(tushare_token)
