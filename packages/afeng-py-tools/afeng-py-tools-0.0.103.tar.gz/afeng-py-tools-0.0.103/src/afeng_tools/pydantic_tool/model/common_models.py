from typing import Optional, Any

from pydantic import BaseModel, Field


class EnumItem(BaseModel):
    # 标题
    title: str = Field(default=None, title='枚举标题')
    value: Optional[str] = Field(default=None, title='枚举值')
    data_dict: Optional[dict[str, Any]] = Field(title='数据字典', default=dict())


class LinkItem(EnumItem):
    """链接项"""
    href: str = Field(title='链接地址')
    title: str = Field(title='链接标题')
    code: Optional[str | int] = Field(default=None, title='编码')
    desc: Optional[str] = Field(default=None, title='链接描述')
    image: Optional[str] = Field(default=None, title='链接图片')
    icon: Optional[str] = Field(default=None, title='链接图标')
    is_active: Optional[bool] = Field(title='是否激活', default=False)
    children: Optional[list['LinkItem']] = Field(title='子项', default=[])
    data_dict: Optional[dict[str, str | int | float]] = Field(title='数据字典', default=dict())
