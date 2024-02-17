from sqlalchemy import Connection, text, select, func

from afeng_tools.sqlalchemy_tool.core.sqlalchemy_session_decorator import auto_conn, auto_commit_conn


@auto_conn()
def query_by_sql(sql, conn: Connection = None):
    """通过sql语句查找"""
    cursor = conn.execute(text(sql))
    return cursor.fetchall()


@auto_commit_conn()
def exec_by_sql(sql, conn: Connection = None):
    """通过sql运行"""
    cursor = conn.execute(text(sql))
    return cursor.lastrowid


def test(model_class, db):
    # select([func.count("*")]).select_from(dataset_no_autoinc)
    select(
        [func.count(model_class.id)], func.length(model_class.name) == 5
    ).execute().first()

    stmt = db.insert().from_select(("data",), select([model_class.data]))
