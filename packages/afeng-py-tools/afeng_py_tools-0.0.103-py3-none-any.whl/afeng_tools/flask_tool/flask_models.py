from flask import Blueprint
from pydantic import BaseModel


class UrlPatternItem(BaseModel):
    """url配置项"""
    # url前缀
    url_prefix: str
    # 路由
    blueprint: Blueprint
