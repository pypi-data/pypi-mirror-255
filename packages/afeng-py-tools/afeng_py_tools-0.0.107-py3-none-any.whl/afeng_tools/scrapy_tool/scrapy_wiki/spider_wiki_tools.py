from typing import Callable

from scrapy import Selector
from scrapy.http import Response

from afeng_tools.scrapy_tool import scrapy_selector_tools
from afeng_tools.scrapy_tool.scrapy_selector_tools import select_first_value
from afeng_tools.scrapy_tool.scrapy_wiki.spider_wiki_items import WikiInfoRuleItem, WikiItemResult


def _handle_wiki_page_child_item(response: Response, selector: Selector, rule_item: WikiInfoRuleItem,
                                 item_result: WikiItemResult) -> list[WikiItemResult]:
    result_list = []
    child_item_el_list = scrapy_selector_tools.select(selector, rule_item.child_item_list_rule)
    if child_item_el_list:
        for child_item_index, child_item_el in enumerate(child_item_el_list):
            child_item_result_list = handle_wiki_page(response, selector=child_item_el,
                                                      rule_item=rule_item.child_item_info_rule,
                                                      parent_item_result=item_result)
            result_list.extend(child_item_result_list)
            if rule_item.is_recursion:
                result_list.extend(
                    _handle_wiki_page_child_item(response, child_item_el, rule_item, child_item_result_list[-1]))

    return result_list


def handle_wiki_page(response: Response, selector: Selector, rule_item: WikiInfoRuleItem,
                     parent_item_result: WikiItemResult = None) -> list[WikiItemResult]:
    """处理wiki的page页面"""
    result_list = []
    title = select_first_value(selector, rule_item.title_rule)
    url = select_first_value(selector, rule_item.url_rule)
    if parent_item_result:
        item_result = parent_item_result.model_copy(deep=True)
    else:
        item_result = WikiItemResult()
    item_result.title_list.append(title)
    item_result.source_url_list.append(url)
    if url:
        url = response.urljoin(url)
    item_result.url_list.append(url)
    item_result.content_rule = rule_item.page_content_rule
    result_list.append(item_result)
    if rule_item.child_item_list_rule and rule_item.child_item_info_rule:
        result_list.extend(_handle_wiki_page_child_item(response, selector, rule_item, item_result))
    return result_list


def has_value(data_list: list[WikiItemResult], new_value: WikiItemResult,
              equal_callback: Callable[[WikiItemResult, WikiItemResult], bool] = lambda x, y: '/'.join(
                  x.title_list) == '/'.join(y.title_list)) -> tuple[bool, int]:
    """
    判断列表中是否有item项
    :param data_list: item列表
    :param new_value: 需要判断是否存在的值
    :param equal_callback: 相等判断函数
    :return: (是否存在，位置索引)
    """
    for index, old_data in enumerate(data_list):
        if equal_callback(old_data, new_value):
            return True, index
    return False, -1


def get_insert_index(start_index: int, data_list: list[WikiItemResult],
                     equal_value_callback: Callable[[WikiItemResult], str] = lambda x: '/'.join(x.title_list)):
    """
    获取插入值的索引
    :param start_index: 开始索引
    :param data_list: 数据列表
    :param equal_value_callback: 判断相等的值回调
    :return:
    """
    tmp_title = equal_value_callback(data_list[start_index])
    tmp_data_list = data_list[start_index:]
    for index, tmp_data in enumerate(tmp_data_list):
        if not equal_value_callback(tmp_data).startswith(tmp_title):
            return start_index + index
    return start_index + len(tmp_data_list) + 1
