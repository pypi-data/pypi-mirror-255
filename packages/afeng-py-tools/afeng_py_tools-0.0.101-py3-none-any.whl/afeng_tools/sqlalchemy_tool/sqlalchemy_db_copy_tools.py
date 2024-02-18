"""
sqlalchemy数据库复制工具
"""
from typing import Callable, Any, Type
from sqlalchemy.orm import Session

from afeng_tools.sqlalchemy_tool.core import sqlalchemy_model_utils
from afeng_tools.sqlalchemy_tool.core.sqlalchemy_db_tools import SqlalchemyDbTool
from afeng_tools.sqlalchemy_tool.core.sqlalchemy_item import DatabaseInfoItem


def create_db_tool(database_uri: str):
    return SqlalchemyDbTool(DatabaseInfoItem(database_uri=database_uri))


def run_db_query(db_tool: SqlalchemyDbTool, query_callback: Callable[[Session, ...], Any], **kwargs) -> Any:
    if 'session' in kwargs:
        return query_callback(**kwargs)
    with db_tool.get_session() as session:
        kwargs['session'] = session
        return query_callback(**kwargs)


class DatabaseCopyTool:
    """数据库数据拷贝工具"""

    def __init__(self, source_database_uri: str, target_database_uri: str):
        self.source_db_tool = create_db_tool(source_database_uri)
        self.target_db_tool = create_db_tool(target_database_uri)

    def query_source_db_data(self, query_callback: Callable[[Session], Any], **kwargs) -> Any:
        """查询源数据库数据"""
        return run_db_query(db_tool=self.source_db_tool, query_callback=query_callback, **kwargs)

    def query_target_db_data(self, query_callback: Callable[[Session], Any], **kwargs) -> Any:
        """查询目标数据库数据"""
        return run_db_query(db_tool=self.target_db_tool, query_callback=query_callback, **kwargs)

    def query_source_db_model_list(self, model_class: Type, *criterion) -> list[Any]:
        """查询源数据库的模型列表"""

        def fun_wrap(session: Session) -> list[Any]:
            if criterion:
                return session.query(model_class).filter(*criterion).all()
            return session.query(model_class).all()

        return self.query_source_db_data(query_callback=fun_wrap)

    def query_target_db_model_list(self, model_class: Type, *criterion) -> list[Any]:
        """查询目标数据库的模型列表"""

        def fun_wrap(session: Session) -> list[Any]:
            if criterion:
                return session.query(model_class).filter(*criterion).all()
            return session.query(model_class).all()

        return self.query_target_db_data(query_callback=fun_wrap)

    def save_target_data(self, model, *criterion, exist_update: bool = True, is_commit: bool = True):
        """保存目标数据库数据"""

        def fun_wrap(session: Session):
            if criterion:
                db_query = session.query(type(model)).where(*criterion)
            else:
                db_query = session.query(type(model)).where(type(model).id.__eq__(model.id))
            old_data = db_query.first()
            if old_data:
                if exist_update:
                    db_query.update(sqlalchemy_model_utils.to_dict(model))
                    if is_commit:
                        session.commit()
                    return db_query.first()
                else:
                    return old_data
            else:
                session.add(model)
                session.flush()
                if is_commit:
                    session.commit()
                return model

        return self.query_target_db_data(query_callback=fun_wrap)


if __name__ == '__main__':
    db_copy_tool = DatabaseCopyTool(source_database_uri='postgresql://postgres:123456@127.0.0.1:5432/test1-db',
                                    target_database_uri='postgresql://postgres:123456@127.0.0.1:5432/test2-db')

    print('*' * 20, '复制分组信息', '*' * 20)
    # old_po.GroupInfoPo和 new_po.GroupInfoPo都应该是Model类，不需要单引号括起来，这里是因为没有这些Model类，做个测试示例
    old_group_list = db_copy_tool.query_source_db_model_list('old_po.GroupInfoPo')
    for old_group in old_group_list:
        new_group = sqlalchemy_model_utils.copy_model_data(old_group, 'new_po.GroupInfoPo')
        db_copy_tool.save_target_data(new_group)
