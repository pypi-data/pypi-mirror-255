from sqlalchemy.orm import Session
from sqlalchemy.sql.ddl import DropSequence, CreateSequence
from sqlalchemy import Connection, select, func, Sequence

from afeng_tools.sqlalchemy_tool.core.sqlalchemy_session_decorator import auto_commit_db


@auto_commit_db()
def create_sequence(sequence_name: str, db: Session = None):
    # create sequence {sequence_name} start with 1 increment by 1 nocache nocycle
    db.execute(CreateSequence(Sequence(name=sequence_name, start=1, increment=1, cycle=False, cache=False),
                              if_not_exists=True))


@auto_commit_db()
def drop_sequence(sequence_name: str, db: Session = None):
    db.execute(DropSequence(Sequence(sequence_name)))


@auto_commit_db()
def get_sequence_next_value(sequence_name: str, db: Session = None) -> int:
    """获取序列的下一个值"""
    result = db.execute(select(func.next_value(Sequence(sequence_name))))
    return result.first()[0]


@auto_commit_db()
def update_sequence_value_to(sequence_name: str, to_value: int, db: Session = None):
    """
    更新序列值到某个值
    :param sequence_name: 序列名
    :param to_value: 要到的值
    :return:
    """
    now_value = get_sequence_next_value(sequence_name, db=db)
    for i in range(now_value, to_value + 1):
        result = get_sequence_next_value(sequence_name, db=db)
        if result == to_value:
            break
