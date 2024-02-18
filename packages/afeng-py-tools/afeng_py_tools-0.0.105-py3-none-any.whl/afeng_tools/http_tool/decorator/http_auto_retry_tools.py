"""
http自动重试工具
"""
import time
from typing import Callable

from afeng_tools.log_tool.loguru_tools import get_logger, log_error

logger = get_logger()


def auto_retry(max_retries: int, retry_delay: float = 0.5):
    """
    自动重试装饰器
    :param max_retries: 最大重试次数
    :param retry_delay: 延迟多少秒重试
    :return: func_wrap
    """
    def func_wrap(func: Callable):
        def func_inner(*args, **kwargs):
            try:
                if isinstance(func, Callable):
                    result = func(*args, **kwargs)
                else:
                    result = func.__func__(*args, **kwargs)
                return result
            except Exception as e:
                log_error(logger, f'[http-retry-{max_retries}][{func.__name__}]-[{args}]-[{kwargs}]', e)
                if max_retries > 0:
                    time.sleep(retry_delay)
                    return auto_retry(max_retries=max_retries - 1, retry_delay=retry_delay)(func)(*args, **kwargs)
                else:
                    raise e
        return func_inner
    return func_wrap
