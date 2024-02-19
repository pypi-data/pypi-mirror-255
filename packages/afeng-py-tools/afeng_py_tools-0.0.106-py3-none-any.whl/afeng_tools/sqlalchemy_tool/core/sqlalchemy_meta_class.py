import re
from copy import copy

from sqlalchemy import Column, Sequence
from sqlalchemy.orm import DeclarativeMeta

from afeng_tools.log_tool import loguru_tools
from afeng_tools.sqlalchemy_tool.core.sqlalchemy_db_tools import SqlalchemyDbTool


class ModelMetaClass(DeclarativeMeta):
    """模型类的元类"""
    logger = loguru_tools.get_logger()

    def __new__(self, name, bases, attrs, **kwargs):
        self._check_class_name_(name, bases, attrs)
        if SqlalchemyDbTool.is_postgresql:
            self._init_sequence_(name, bases, attrs)
        super_new = super().__new__
        parents = [b for b in bases if isinstance(b, ModelMetaClass)]
        if not parents:
            return super_new(self, name, bases, attrs)
        # 将类字段添加到columns中
        column_dict = dict()
        for p in parents:
            for k, v in p.__dict__.items():
                if isinstance(v, Column):
                    column_dict[k] = v
        for k, v in attrs.items():
            if isinstance(v, Column):
                column_dict[k] = v
        new_class = super_new(self, name, bases, attrs, **kwargs)
        setattr(new_class, '__column_dict__', column_dict)
        return new_class

    @classmethod
    def _init_sequence_(cls, class_name, class_bases, class_attrs):
        """初始化序列"""
        parents = [b for b in class_bases if isinstance(b, ModelMetaClass)]
        if not parents:
            return
        if SqlalchemyDbTool.is_postgresql:
            sequence_name = class_attrs["__tablename__"] + '_id_seq'
            if 'id' not in class_attrs:
                class_attrs['id'] = copy(getattr(parents[0], 'id'))
            try:
                id_column = class_attrs['id']
                id_column.default = Sequence(name=sequence_name, start=1, increment=1, cycle=False)
            except Exception as ex:
                loguru_tools.log_error(cls.logger, f'创建序列[{sequence_name}]失败', ex)

    @classmethod
    def _check_class_name_(cls, class_name, class_bases, class_attrs):
        """检查类名"""
        parents = [b for b in class_bases if isinstance(b, ModelMetaClass)]
        if not parents:
            return
        if not re.match('[A-Z]', class_name):
            raise TypeError('Model类名[%s]请修改为首字母大写' % class_name)
        if '__doc__' not in class_attrs or len(class_attrs['__doc__'].strip(' \n')) == 0:
            raise TypeError('Model类[%s]中必须有文档注释，并且文档注释不能为空' % class_name)
