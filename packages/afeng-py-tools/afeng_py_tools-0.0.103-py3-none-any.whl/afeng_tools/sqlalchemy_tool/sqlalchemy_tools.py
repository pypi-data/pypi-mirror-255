"""
sqlalchemy工具
"""
from typing import Callable

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def create_session_maker(database_uri, echo: bool = True, pool_size: int = 50) -> sessionmaker[Session]:
    """
    创建 SessionMaker
    :param database_uri: 数据库连接地址，如： 'mysql://root:123456@127.0.0.1:3306/video_tools_db'
    :param echo: 是否打印sql
    :param pool_size: 连接池大小
    :return: SessionMaker, 用于创建Session，如：SessionMaker = create_SessionMaker(database_uri); session = SessionMaker()
    """
    return sessionmaker(bind=create_engine(database_uri, echo=echo, pool_size=pool_size),
                        autocommit=False,
                        autoflush=False,
                        expire_on_commit=False)


def create_session(database_uri) -> Session:
    """创建数据库Session"""
    return create_session_maker(database_uri)()


def get_session(session_maker: sessionmaker[Session]) -> Session:
    """获取数据库Session"""
    with session_maker.begin() as session:
        return session


def database_copy_data(database_uri1: str, database_uri2: str, execute_business_fun: Callable, echo: bool = False):
    """
    数据库复制数据
    :param database_uri1: 数据库连接1
    :param database_uri2: 数据库连接2
    :param execute_business_fun: 执行复制业务的函数，该函数需要有两个参数：session1,session2
    :param echo: 是否打印sql
    :return:
    """
    session1 = create_session_maker(database_uri1, echo=echo)()
    session2 = create_session_maker(database_uri2, echo=echo)()
    try:
        execute_business_fun(session1, session2)
    finally:
        session1.close()
        session2.close()