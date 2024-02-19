from sqlalchemy import Connection, text, select, func

from afeng_tools.sqlalchemy_tools.decorator.sqlalchemy_session_decorator import auto_conn, auto_commit_conn


@auto_conn()
def query_by_sql(sql: str, conn: Connection = None):
    """通过sql语句查找"""
    cursor = conn.execute(text(sql))
    return cursor.fetchall()


@auto_commit_conn()
def exec_by_sql(sql: str, conn: Connection = None):
    """通过sql运行"""
    cursor = conn.execute(text(sql))
    return cursor.lastrowid
