import re

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from afeng_tools.sqlalchemy_tool.core.sqlalchemy_item import DatabaseInfoItem

# 创建一个Base类
Base = declarative_base()


class SqlalchemyDbTool:
    """db工具类"""
    is_postgresql = True

    def __init__(self, database_info: DatabaseInfoItem):
        self.database_info = database_info
        self.engine = None
        self.session_maker = None
        self._create_engine()
        self._create_session_maker()
        self.is_postgresql = self.get_is_postgresql()

    def _create_engine(self):
        """创建engine"""
        self.engine = create_engine(self.database_info.database_uri,
                                    echo=self.database_info.echo_sql,
                                    pool_size=self.database_info.pool_size,
                                    pool_pre_ping=True, pool_recycle=3600, pool_use_lifo=True)

    def _create_session_maker(self):
        """Session创建者"""
        self.session_maker = sessionmaker(bind=self.engine,
                                          autocommit=self.database_info.auto_commit,
                                          autoflush=self.database_info.auto_flush,
                                          expire_on_commit=self.database_info.expire_on_commit)

    def get_session(self) -> Session:
        """获取Session"""
        return self.session_maker()

    def get_is_postgresql(self) -> bool:
        """是否是postgresql"""
        return True if re.match('^postgresql', self.database_info.database_uri) else False
