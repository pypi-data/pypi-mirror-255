from typing import Callable, Any
from scrapy import Selector
from scrapy.http import HtmlResponse, Response
from scrapy.selector import SelectorList

from afeng_tools.scrapy_tool import scrapy_selector_tools
from afeng_tools.scrapy_tool.scrapy_selector_tools import select_first_value
from afeng_tools.scrapy_tool.scrapy_wiki.spider_wiki_items import WikiInfoRuleItem, HandleWikiPageResult, \
    HandleWikiRequestItem


def handle_wiki_page(response: HtmlResponse, selector: Response | Selector | SelectorList,
                     rule_item: WikiInfoRuleItem,
                     item_callback: Callable[[Any, Any, ...], HandleWikiPageResult],
                     **kwargs) -> list[HandleWikiRequestItem]:
    """处理wiki的page页面"""
    request_list = []
    kwargs['title'] = select_first_value(selector, rule_item.title_rule)
    kwargs['url'] = response.urljoin(select_first_value(selector, rule_item.url_rule))
    item_result = item_callback(**kwargs)
    if kwargs['url'] and item_result.has_request:
        if item_result.request_kwargs:
            cb_kwargs = item_result.request_kwargs
        else:
            cb_kwargs = dict()
        cb_kwargs['content_rule'] = rule_item.page_content_rule
        request_list.append(HandleWikiRequestItem(
            url=kwargs['url'],
            cb_kwargs=item_result.request_kwargs
        ))
    if rule_item.child_item_list_rule and rule_item.child_item_info_rule and item_result.has_next:
        child_item_el_list = scrapy_selector_tools.select(selector, rule_item.child_item_list_rule)
        if child_item_el_list:
            if item_result.next_callback_kwargs:
                kwargs.update(item_result.next_callback_kwargs)
            for child_item_index, child_item_el in enumerate(child_item_el_list):
                kwargs['child_index'] = child_item_index
                request_list.extend(handle_wiki_page(response,
                                                     selector=child_item_el,
                                                     rule_item=rule_item.child_item_info_rule,
                                                     item_callback=item_callback,
                                                     **kwargs))
    return request_list
