"""
爬虫item
"""
from typing import Optional

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


class WikiItemResult(BaseModel):
    """wiki爬虫单项结果"""
    # 标题列表，是分级别的
    title_list: Optional[list[str]] = []
    # 标题路径列表，对应上面的标题列表
    url_list: Optional[list[str]] = []
    # 标题路径列表，对应上面的标题列表
    source_url_list: Optional[list[str]] = []
    # 页面内容获取规则
    content_rule: Optional[str] = None
    # 保存的html文件名
    html_file_name: Optional[str] = None
    # html路径锚点
    html_url_anchor: Optional[str] = None


