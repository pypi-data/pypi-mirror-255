from typing import Optional

from pydantic import BaseModel


class DatabaseInfoItem(BaseModel):
    """数据库信息项"""
    # 数据库连接地址
    database_uri: str
    # 是否打印sql
    echo_sql: Optional[bool] = False
    # 数据库连接池
    pool_size: Optional[int] = 0
    # 是否自动提交
    auto_commit: Optional[bool] = False
    # 是否自动flush
    auto_flush: Optional[bool] = False
    # 超时是否自动提交
    expire_on_commit: Optional[bool] = False

