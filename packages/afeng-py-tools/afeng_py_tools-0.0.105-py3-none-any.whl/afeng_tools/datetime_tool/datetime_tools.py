"""
日期时间工具
"""
from datetime import datetime
import time


def get_today(time_formate: str = '%Y%m%d'):
    """获取当日的日期字符串"""
    return datetime.today().strftime(time_formate)


def get_now(time_formate: str = '%Y-%m-%d %H:%M:%S') -> str:
    """获取当前时间符串"""
    return datetime.now().strftime(time_formate)


def get_timestamp() -> int:
    """获取时间戳"""
    return int(time.time())


def get_time_str(time_formate: str = '%Y%m%d%H%M%S%f') -> str:
    """获取时间字符串"""
    return datetime.now().strftime(time_formate)


def get_now_info():
    """获取现在的信息"""
    now_time = datetime.now()
    year = ('000' + str(now_time.year))[-4:]
    month = ('0' + str(now_time.month))[-2:]
    day = ('0' + str(now_time.day))[-2:]
    hour = ('0' + str(now_time.hour))[-2:]
    minute = ('0' + str(now_time.minute))[-2:]
    second = ('0' + str(now_time.second))[-2:]
    return year, month, day, hour, minute, second


if __name__ == '__main__':
    print(get_today())
