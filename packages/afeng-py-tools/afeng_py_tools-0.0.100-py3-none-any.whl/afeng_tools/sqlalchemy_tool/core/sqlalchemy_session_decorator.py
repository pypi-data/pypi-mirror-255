from afeng_tools.decorator_tool.decorator_tools import run_func
from afeng_tools.log_tool import loguru_tools
from afeng_tools.log_tool.loguru_tools import log_error
from afeng_tools.sqlalchemy_tool import sqlalchemy_settings

logger = loguru_tools.get_logger()


def auto_commit_db(db_code: str = 'default', retry: int = 0):
    """自动注入自动提交的db: Session"""
    def auto_wrap(func):
        def wrap(*args, **kwargs):
            if 'db' in kwargs:
                return run_func(func, *args, **kwargs)
            with sqlalchemy_settings.get_database_tool(db_code=db_code).get_session() as session:
                try:
                    kwargs['db'] = session
                    result = run_func(func, *args, **kwargs)
                    session.commit()
                    return result
                except Exception as e:
                    log_error(logger, f'[Db session commit data exception]', e)
                    session.rollback()
                    if retry > 0:
                        kwargs.pop('db')
                        return auto_commit_db(db_code, retry - 1)(func)(*args, **kwargs)
        return wrap
    return auto_wrap


def auto_db(db_code: str = 'default'):
    """自动注入db: Session"""
    def auto_wrap(func):
        def wrap(*args, **kwargs):
            if 'db' in kwargs:
                return run_func(func, *args, **kwargs)
            with sqlalchemy_settings.get_database_tool(db_code=db_code).get_session() as session:
                kwargs['db'] = session
                return run_func(func, *args, **kwargs)

        return wrap

    return auto_wrap


def auto_commit_conn(db_code: str = 'default'):
    """自动注入自动提交的conn: Connection"""

    def auto_wrap(func):
        def wrap(*args, **kwargs):
            if 'conn' in kwargs:
                return run_func(func, *args, **kwargs)
            with sqlalchemy_settings.get_database_tool(db_code=db_code).engine.connect() as conn:
                try:
                    kwargs['conn'] = conn
                    result = run_func(func, *args, **kwargs)
                    conn.commit()
                    return result
                except Exception as e:
                    log_error(logger, f'[Db connection commit data exception]', e)
                    conn.rollback()

        return wrap

    return auto_wrap


def auto_conn(db_code: str = 'default'):
    """自动注入conn: Connection"""

    def auto_wrap(func):
        def wrap(*args, **kwargs):
            if 'conn' in kwargs:
                return run_func(func, *args, **kwargs)
            with sqlalchemy_settings.get_database_tool(db_code=db_code).engine.connect() as conn:
                kwargs['conn'] = conn
                return run_func(func, *args, **kwargs)

        return wrap

    return auto_wrap
