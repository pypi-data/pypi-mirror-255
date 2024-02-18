"""
时间监视器工具
"""
import time
from typing import Callable


def time_monitor(func):
    """装饰器：时间监视器，用于统计执行消耗时间"""

    def func_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        if isinstance(func, Callable):
            result = func(*args, **kwargs)
        else:
            result = func.__func__(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f'[{func.__name__}]-[use time ：{execution_time}]')
        return result

    return func_wrapper
