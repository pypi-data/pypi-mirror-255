"""
sqlalchemy设置
"""
# 数据库字典
__DATABASE_DICT_CACHE__ = dict()

from afeng_tools.sqlalchemy_tools.core.sqlalchemy_class import SqlalchemyDb
from afeng_tools.sqlalchemy_tools.core.sqlalchemy_items import DatabaseInfoItem


def set_database(database_info: DatabaseInfoItem, db_code: str = 'default'):
    """
    设置数据库工具
    :param database_info: 数据库信息
    :param db_code: 数据库编码
    :return:
    """
    __DATABASE_DICT_CACHE__[db_code] = SqlalchemyDb(database_info)


def get_database(db_code: str = 'default') -> SqlalchemyDb:
    """
    获取数据库工具
    :param db_code: 数据库编码
    :return: SqlalchemyDbTool
    """
    db_tool = __DATABASE_DICT_CACHE__.get(db_code)
    if db_tool is None:
        raise RuntimeError(
            '数据库配置缺失！请使用set_database_tool(DatabaseInfoItem(database_uri="postgresql://postgres:123456@127.0.0.1:5432/book-room-db"))进行数据库配置！')
    return db_tool
