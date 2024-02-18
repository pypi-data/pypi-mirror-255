from typing import Callable, Any

from sqlalchemy import BinaryExpression, ColumnElement, LambdaElement

from sqlalchemy.orm import Session, Query

from afeng_tools.sqlalchemy_tool.core.sqlalchemy_base_model import Model
from afeng_tools.sqlalchemy_tool.core.sqlalchemy_meta_class import ModelMetaClass
from afeng_tools.sqlalchemy_tool.core.sqlalchemy_model_utils import to_dict
from afeng_tools.sqlalchemy_tool.core.sqlalchemy_enums import SortTypeEnum
from afeng_tools.sqlalchemy_tool.core.sqlalchemy_session_decorator import auto_commit_db, auto_db


@auto_commit_db()
def add(model, db: Session = None):
    db.add(model)
    db.flush()
    return model


@auto_commit_db()
def add_all(model_list: list, db: Session = None) -> list:
    for tmp_model in model_list:
        add(tmp_model, db=db)
    return model_list


@auto_commit_db()
def create_commit_query(model_class, callback: Callable, *criterion, db: Session = None) -> Any:
    """
    创建提交的query
    :param model_class: model类
    :param callback: 回调函数，用于传入 Query
    :param criterion: Query条件， 如：CategoryInfo.id <= 280
    :param db: 自动导入的db
    :return: 回调函数的结果，Any
    """
    if criterion:
        db_query = db.query(model_class).filter(*criterion)
    else:
        db_query = db.query(model_class)
    return callback(db_query)


def create_id_criterion(model: Any) -> ColumnElement[bool]:
    return type(model).id.__eq__(model.id)


@auto_commit_db()
def update(model, *criterion, db: Session = None):
    if criterion:
        db_query = db.query(type(model)).filter(*criterion)
    else:
        db_query = db.query(type(model)).filter(create_id_criterion(model))
    db_query.update(to_dict(model))
    return db_query.first()


@auto_commit_db()
def update_batch(model_list: list, db: Session = None):
    for tmp_model in model_list:
        create_commit_query(type(tmp_model), lambda q: q.update(to_dict(tmp_model)),
                            type(tmp_model).id == tmp_model.id,
                            db=db)
    return model_list


@auto_commit_db(retry=3)
def save(model, *criterion, db: Session = None, exist_update: bool = True):
    if criterion:
        db_query = db.query(type(model)).where(*criterion)
    else:
        db_query = db.query(type(model)).where(create_id_criterion(model))
    old_data = db_query.first()
    if old_data:
        if exist_update:
            db_query.update(to_dict(model))
            return db_query.first()
        else:
            return old_data
    else:
        return add(model, db=db)


@auto_commit_db()
def save_batch_by_where(model_list: list, criterion_fun: Callable, db: Session = None,
                        exist_update: bool = True) -> list:
    """
    批量存在更新记录，否则插入记录
    :param model_list: Model数据列表
    :param criterion_fun:  通过接受model，返回判断条件, 如：lambda x: type(x).ts_code == x.ts_code
    :param db: 自动注入的Session
    :param exist_update: 如果存在则更新，如果为False，则如果存在则啥也不做
    :return: Model数据列表
    """
    for tmp_model in model_list:
        criterion = criterion_fun(tmp_model)
        if not criterion and tmp_model.id:
            criterion = type(tmp_model).id == tmp_model.id
        if type(criterion) == BinaryExpression:
            criterion = (criterion,)
        if criterion and db.query(type(tmp_model)).filter(*criterion).count() > 0:
            if exist_update:
                update(tmp_model, *criterion, db=db)
        else:
            add(tmp_model, db=db)
    return model_list


@auto_commit_db()
def add_all(model_list: list, db: Session = None) -> list:
    for tmp_model in model_list:
        add(tmp_model, db=db)
    return model_list


@auto_commit_db()
def delete_by_model(model, db: Session = None):
    db.delete(model)
    return model


@auto_commit_db()
def delete(model, *criterion, db: Session = None):
    """
    删除记录
    :param criterion: 删除条件如：CategoryInfo.id <= 280， 默认按照id删除
    :return:
    """
    if criterion:
        model_class = type(model)
        if issubclass(type(model), Model):
            model_class = type(model)
        elif issubclass(type(model), ModelMetaClass):
            model_class = model
        db.query(model_class).filter(*criterion).delete()
    else:
        db.query(type(model)).filter(create_id_criterion(model)).delete()
    return True


@auto_commit_db()
def delete_by_class(model_class, *criterion, db: Session = None):
    """
    删除记录
    :param criterion: 删除条件如：CategoryInfo.id <= 280， 默认按照id删除
    :return:
    """
    if criterion:
        db.query(model_class).filter(*criterion).delete()
    else:
        raise AttributeError('Args [*criterion] can not be None')
    return True


@auto_commit_db()
def delete_by_ids(model_class, ids: list[int], db: Session = None):
    """根据id批量删除"""
    db.query(model_class).filter(model_class.id.in_(ids)).delete()


@auto_db()
def get_by_id(model_class, id_value: int, db: Session = None):
    return db.get(model_class, id_value)


@auto_db()
def create_query(model_class, *criterion, db: Session = None) -> Query:
    if criterion:
        return db.query(model_class).filter(*criterion)
    else:
        return db.query(model_class)


@auto_db()
def query_all(model_class, *criterion, db: Session = None,
              sort_column: str = 'order_num', sort_type: SortTypeEnum = SortTypeEnum.desc) -> list:
    if sort_type == SortTypeEnum.desc:
        _order_by = getattr(model_class, sort_column).desc()
    else:
        _order_by = getattr(model_class, sort_column).asc()
    return create_query(model_class, *criterion, db=db).order_by(_order_by).all()


@auto_db()
def query_one(model_class, *criterion, db: Session = None,
              sort_column: str = None, sort_type: SortTypeEnum = SortTypeEnum.desc):
    """根据 where条件查询一条记录"""
    db_query = create_query(model_class, *criterion, db=db)
    if sort_column:
        if sort_type == SortTypeEnum.desc:
            _order_by = getattr(model_class, sort_column).desc()
        else:
            _order_by = getattr(model_class, sort_column).asc()
        db_query = db_query.order_by(_order_by)
    return db_query.first()


def query_by_ids(model_class, id_list: list[int]) -> list:
    """通过id集合查询"""
    return query_all(model_class, type(model_class).id.in_(id_list))


@auto_db()
def query_page(model_class, page_num, page_size, *criterion, db: Session = None,
               sort_column: str = 'order_num', sort_type: SortTypeEnum = SortTypeEnum.desc):
    """分页查询"""
    start_index = (page_num - 1) * page_size
    if sort_type == SortTypeEnum.desc:
        _order_by = getattr(model_class, sort_column).desc()
    else:
        _order_by = getattr(model_class, sort_column).asc()
    return create_query(model_class, *criterion, db=db).order_by(_order_by).offset(start_index).limit(page_size).all()


@auto_db()
def count(model_class, *criterion, db: Session = None) -> int:
    """查询记录数"""
    return create_query(model_class, *criterion, db=db).count()
