"""
sqlalchemy设置
"""
from afeng_tools.sqlalchemy_tool.core.sqlalchemy_db_tools import SqlalchemyDbTool
from afeng_tools.sqlalchemy_tool.core.sqlalchemy_item import DatabaseInfoItem

# 数据库字典
__DATABASE_DICT_CACHE__ = dict()


def set_database_tool(database_info: DatabaseInfoItem, db_code: str = 'default'):
    """
    设置数据库工具
    :param database_info: 数据库信息
    :param db_code: 数据库编码
    :return:
    """
    __DATABASE_DICT_CACHE__[db_code] = SqlalchemyDbTool(database_info)


def get_database_tool(db_code: str = 'default') -> SqlalchemyDbTool:
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
