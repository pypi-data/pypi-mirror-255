"""
交易日历-工具：
- pip install pandas
- pip install exchange_calendars
"""

from datetime import datetime, timedelta

import exchange_calendars
from pandas import Timestamp

sh_calendar = exchange_calendars.get_calendar("XSHG", side='both')


def next_trade_date(date: str = None) -> str:
    """
    下一个交易日
    :param date: 日期，如：2023-09-12
    :return: 下一个交易日
    """
    if not date:
        trade_time = datetime.now() - timedelta(hours=1)
        timestamp = Timestamp(trade_time.strftime('%Y-%m-%d %H:%M:%S'), tz="Asia/Shanghai")
    else:
        timestamp = Timestamp(f'{date} 23:59:59', tz="Asia/Shanghai")
    return sh_calendar.date_to_session(timestamp, direction="next", _parse=False).strftime("%Y-%m-%d")


def previous_trade_date(date: str = None) -> str:
    """
    上一个交易日
    :param date: 日期，如：2023-09-12
    :return: 上一个交易日
    """
    if not date:
        trade_time = datetime.now() - timedelta(hours=1)
        timestamp = Timestamp(trade_time.strftime('%Y-%m-%d %H:%M:%S'), tz="Asia/Shanghai")
    else:
        timestamp = Timestamp(f'{date} 00:00:00', tz="Asia/Shanghai")
    return sh_calendar.date_to_session(timestamp, direction="previous", _parse=False).strftime("%Y-%m-%d")


if __name__ == '__main__':
    # print(next_trade_date('2023-09-12'))
    # print(previous_trade_date('2023-09-11'))
    # print(previous_trade_date('2023-09-19'))
    print(previous_trade_date())
    print(next_trade_date())

