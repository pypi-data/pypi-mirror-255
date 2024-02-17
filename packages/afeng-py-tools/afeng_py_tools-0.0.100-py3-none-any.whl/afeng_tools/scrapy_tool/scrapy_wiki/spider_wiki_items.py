"""
爬虫item
"""
from typing import Optional, Any

from pydantic import BaseModel


class WikiInfoRuleItem(BaseModel):
    """Wiki信息规则项"""
    # 文本规则
    title_rule: Optional[str] = None
    # 链接规则
    url_rule: Optional[str] = None
    # url请求的页面内容规则
    page_content_rule: Optional[str] = None
    # 子项列表规则
    child_item_list_rule: Optional[str] = None
    # 子项信息规则项
    child_item_info_rule: Optional['WikiInfoRuleItem'] = None
    # 是否递归
    is_recursion: bool = False


class HandleWikiPageResult(BaseModel):
    """处理Wiki页面结果"""
    # 是否有request请求
    has_request: bool = True
    # request参数
    request_kwargs: Optional[dict[str, Any]] = None
    # 是否有下一步
    has_next: bool = True
    # 下一次callback参数
    next_callback_kwargs: Optional[dict[str, Any]] = None
    pass


class HandleWikiRequestItem(BaseModel):
    """处理wiki的request项"""
    # 链接
    url: Optional[str] = None
    # request的参数
    cb_kwargs: Optional[dict[str, Any]] = None
