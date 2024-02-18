"""
scrapy的selector工具
"""
from typing import Any

from scrapy import Selector
from scrapy.http import Response
from scrapy.selector import SelectorList


def select(selector: Response | Selector, selector_value: str) -> None | Selector | SelectorList | list[Selector]:
    """选择元素"""
    if selector_value is None:
        return None
    if selector_value.startswith('./') or selector_value.startswith('/'):
        return selector.xpath(selector_value)
    else:
        return selector.css(selector_value)


def extract_first(selector: Selector | SelectorList) -> Any:
    """提取第一个元素值"""
    if selector:
        value = selector.extract_first()
        if value and isinstance(value, str):
            return value.strip()
        return value


def select_first_value(selector: Response | Selector, selector_value: str) -> Any:
    """选择第一个元素的值"""
    return extract_first(select(selector, selector_value))
