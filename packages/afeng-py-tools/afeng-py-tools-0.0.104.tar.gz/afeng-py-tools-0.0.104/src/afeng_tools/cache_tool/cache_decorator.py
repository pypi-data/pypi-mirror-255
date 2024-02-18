"""
换成解释器
"""
import time
from functools import wraps

# 内存缓存
MEMORY_CACHE = {}


def cache_with_expiration(expiration: int):
    """
    cache_with_expiration 是一个装饰器，它接受一个参数 expiration，表示缓存的过期时间（以秒为单位）。
        - 当 expensive_function 被调用时，它的结果会被缓存起来，并附带一个时间戳。下次再调用 expensive_function 时，如果参数相同，那么就直接返回缓存的结果。
        - 如果参数不同，或者缓存已经过期（即距离上次函数调用已经超过 expiration 秒），那么就会重新计算结果，并更新缓存。
    :param expiration:
    :return:
    """
    def inner_func(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = str(func.__qualname__) + str(args) + str(kwargs)
            result = MEMORY_CACHE.get(key)
            if result is None:
                result = func(*args, **kwargs)
                MEMORY_CACHE[key] = (time.time(), result)
                return result
            else:
                old_timestramp, old_result = result
                if time.time() - old_timestramp > expiration:
                    MEMORY_CACHE.pop(key)
                    result = func(*args, **kwargs)
                    MEMORY_CACHE[key] = (time.time(), result)
                    return result
                else:
                    return old_result

        return wrapper

    return inner_func
