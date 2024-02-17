"""
内存缓存工具
"""
import time
from typing import Any

MEMORY_CACHE = {}


def add_cache(group_code: str, key: str, value: Any):
    """添加缓存"""
    group_cache = MEMORY_CACHE.get(group_code)
    if not group_cache:
        MEMORY_CACHE[group_code] = dict()
    MEMORY_CACHE[group_code][key] = value


def delete_cache(group_code: str, key: str) -> Any:
    """添加缓存"""
    group_cache = MEMORY_CACHE.get(group_code)
    if group_cache:
        return group_cache.pop(key, None)


def get_cache(group_code: str, key: str) -> Any:
    """获取缓存"""
    group_cache = MEMORY_CACHE.get(group_code)
    if group_cache:
        return group_cache.get(key)


def add_time_cache(group_code: str, key: str, value: Any, timestamp: float = None):
    """添加缓存"""
    group_cache = MEMORY_CACHE.get(group_code)
    if not group_cache:
        MEMORY_CACHE[group_code] = dict()
    if timestamp is None:
        timestamp = time.time()
    MEMORY_CACHE[group_code][key] = (timestamp, value)


def get_time_cache(group_code: str, key: str) -> dict[float, Any]:
    """获取缓存: 时间戳，值"""
    group_cache = MEMORY_CACHE.get(group_code)
    if group_cache:
        return group_cache.get(key)
