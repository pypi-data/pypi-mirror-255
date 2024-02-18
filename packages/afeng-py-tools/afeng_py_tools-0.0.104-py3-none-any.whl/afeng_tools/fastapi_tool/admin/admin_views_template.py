import enum
import json
from typing import Type, Any, Optional, Iterable

from fastapi import Form
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import String, func, Text, Boolean, ARRAY
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse

from afeng_tools.fastapi_tool.fastapi_response_tools import resp_json
from afeng_tools.id_code_tool import id_code_tools
from afeng_tools.layui_tool import layui_template_tools
from afeng_tools.layui_tool.core.layui_models import LayUiFormItem, LayUiTableCol, LayUiTableActionItem, LayUiTableData
from afeng_tools.pydantic_tool.model.common_models import EnumItem
from afeng_tools.sqlalchemy_tools.crdu import base_crdu
from afeng_tools.sqlalchemy_tools.tool import orm_model_tools


class AdminViewsTemplate:
    def __init__(self, module_code: str, orm_model_class: Type, search_form_item_list: list[LayUiFormItem],
                 db_code='default'):
        """
        Admin管理Views模板
        :param module_code: 模块编码
        :param orm_model_class: orm模型类
        :param search_form_item_list: 用于查询的表单项列表
        """
        self.module_code = module_code
        self.orm_model_class = orm_model_class
        self.search_form_item_list = search_form_item_list
        self.db_code = db_code

    def _create_form_item_list(self, old_data=None):
        form_item_list = []
        for c in self.orm_model_class.__table__.columns:

            if issubclass(c.type.python_type, enum.Enum):
                tmp_form_item = LayUiFormItem(title=c.comment, name=c.name, type='select',
                                              select_list=[((tmp.value if isinstance(tmp.value, str) else tmp.name),
                                                            tmp.name, False, False) for tmp in
                                                           c.type.python_type])
            elif isinstance(c.type, Boolean):
                tmp_form_item = LayUiFormItem(title=c.comment, name=c.name, type='switch',
                                              switch_item=('1', '开启|关闭', False, False))
            elif isinstance(c.type, ARRAY):
                tmp_form_item = LayUiFormItem(title=c.comment, name=c.name, type='array')
            elif issubclass(c.type.python_type, int):
                tmp_form_item = LayUiFormItem(title=c.comment, name=c.name, type='number')
            elif isinstance(c.type, Text):
                tmp_form_item = LayUiFormItem(title=c.comment, name=c.name, type='textarea')
            else:
                tmp_form_item = LayUiFormItem(title=c.comment, name=c.name)
            if old_data is not None:
                if issubclass(c.type.python_type, enum.Enum):
                    tmp_select_list = []
                    for tmp_value, tmp_title, tmp_selected, tmp_disabled in tmp_form_item.select_list:
                        old_data_field_value = getattr(old_data, c.name)
                        if isinstance(old_data_field_value, enum.Enum):
                            if isinstance(old_data_field_value.value, EnumItem):
                                old_data_field_value = old_data_field_value.value.value
                            else:
                                old_data_field_value = old_data_field_value.value
                        if tmp_value == old_data_field_value:
                            tmp_selected = True
                        tmp_select_list.append((tmp_value, tmp_title, tmp_selected, tmp_disabled))
                    tmp_form_item.select_list = tmp_select_list
                elif isinstance(c.type, Boolean):
                    tmp_value, tmp_title, tmp_checked, tmp_disabled = tmp_form_item.switch_item
                    if getattr(old_data, c.name):
                        tmp_checked = True
                    tmp_form_item.switch_item = (tmp_value, tmp_title, tmp_checked, tmp_disabled)
                elif isinstance(c.type, ARRAY):
                    tmp_value = getattr(old_data, c.name)
                    if tmp_value and isinstance(tmp_value, Iterable):
                        tmp_form_item.default = ','.join([str(tmp) for tmp in tmp_value])
                else:
                    print(type(old_data), c.name)
                    tmp_value = getattr(old_data, c.name)
                    if tmp_value is not None:
                        print(type(tmp_value), c.name)
                        tmp_form_item.default = getattr(old_data, c.name)
            form_item_list.append(tmp_form_item)
        return form_item_list

    async def index_page(self) -> HTMLResponse:
        """列表页面"""
        model_title = self.orm_model_class.__doc__
        col_list = [
            LayUiTableCol(field=c.name, title=c.comment, sort=True, is_enum=issubclass(c.type.python_type, enum.Enum))
            for c in
            self.orm_model_class.__table__.columns]
        return HTMLResponse(layui_template_tools.render_table_template(title=f'{model_title}-管理',
                                                                       search_form_item_list=self.search_form_item_list,
                                                                       data_url=f'/admin/api/{self.module_code}/list',
                                                                       col_list=col_list,
                                                                       add=True,
                                                                       add_html_url=f'/admin/{self.module_code}/add',
                                                                       edit=True,
                                                                       edit_html_url=f'/admin/{self.module_code}/update',
                                                                       delete=True,
                                                                       delete_url=f'/admin/api/{self.module_code}/delete',
                                                                       more_delete=True,
                                                                       more_delete_url=f'/admin/api/{self.module_code}/more_delete',
                                                                       action_list=[
                                                                           LayUiTableActionItem(title='展示',
                                                                                                url=f'/admin/{self.module_code}/show')
                                                                       ]
                                                                       ))

    async def add_page(self) -> HTMLResponse:
        """添加页面"""
        model_title = self.orm_model_class.__doc__
        return HTMLResponse(layui_template_tools.render_add_template(title=f'添加-{model_title}',
                                                                     form_item_list=self._create_form_item_list(),
                                                                     add_url=f'/admin/api/{self.module_code}/add'))

    async def update_page(self, request: Request, id_value: int) -> HTMLResponse:
        """修改页面"""
        model_title = self.orm_model_class.__doc__
        old_data = base_crdu.query_one(self.orm_model_class,
                                       self.orm_model_class.id == id_value,
                                       db_code=self.db_code)
        return HTMLResponse(layui_template_tools.render_edit_template(title=f'修改-{model_title}',
                                                                      form_item_list=self._create_form_item_list(
                                                                          old_data),
                                                                      edit_url=f'/admin/api/{self.module_code}/update'))

    async def show_page(self, request: Request, id_value: int) -> HTMLResponse:
        """展示页面"""
        model_title = self.orm_model_class.__doc__
        old_data = base_crdu.query_one(self.orm_model_class,
                                       self.orm_model_class.id == id_value,
                                       db_code=self.db_code)
        if old_data:
            form_item_list = [
                LayUiFormItem(title=c.comment, name=c.name, default=getattr(old_data, c.name), readonly=True)
                for c in self.orm_model_class.__table__.columns]
        else:
            form_item_list = [LayUiFormItem(title=c.comment, name=c.name)
                              for c in self.orm_model_class.__table__.columns]
        return HTMLResponse(layui_template_tools.render_show_template(title=f'展示-{model_title}',
                                                                      form_item_list=form_item_list))

    async def add_data(self, request: Request, form_data: BaseModel) -> JSONResponse:
        """添加数据"""
        po = orm_model_tools.py_model_to_orm_model(form_data, self.orm_model_class)
        po = base_crdu.add(po, db_code=self.db_code)
        self.add_data_after_handle(po)
        return resp_json(po)

    async def update_data(self, request: Request, form_data: BaseModel) -> JSONResponse:
        """更新数据"""
        po = orm_model_tools.py_model_to_orm_model(form_data, self.orm_model_class)
        po = base_crdu.update(po, db_code=self.db_code)
        self.update_data_after_handle(po)
        return resp_json(po)

    async def delete_data(self, request: Request, id_value: int) -> JSONResponse:
        """删除数据"""
        old_po = base_crdu.query_one(self.orm_model_class, self.orm_model_class.id == id_value,
                                     db_code=self.db_code)
        base_crdu.delete_by_ids(self.orm_model_class, [id_value], db_code=self.db_code)
        self.delete_data_after_handle(old_po)
        return resp_json('success')

    async def more_delete_data(self, request: Request, ids: str = Form()):
        id_list = json.loads(ids)
        old_po_list = base_crdu.query_all(self.orm_model_class, self.orm_model_class.id.in_(id_list),
                                          db_code=self.db_code)
        base_crdu.delete_by_ids(self.orm_model_class, id_list, db_code=self.db_code)
        for old_po in old_po_list:
            self.delete_data_after_handle(old_po)
        return resp_json('success')

    async def get_data(self, request: Request, id_value: int) -> JSONResponse:
        """查询单条数据"""
        return resp_json(base_crdu.query_one(self.orm_model_class, self.orm_model_class.id == id_value,
                                             db_code=self.db_code))

    async def list_data(self, request: Request, page: Optional[int] = 1, limit: Optional[int] = 15,
                        searchParams: Optional[str] = None):
        """列出所有数据"""
        search_params = None
        if searchParams:
            search_params = json.loads(searchParams)
        query = base_crdu.create_query(self.orm_model_class, db_code=self.db_code)
        if search_params:
            search_field_list = [tmp.name for tmp in self.search_form_item_list]
            for tmp_key, tmp_value in search_params.items():
                if tmp_key in search_field_list and tmp_value is not None and len(tmp_value) > 0:
                    query = query.filter(
                        func.cast(getattr(self.orm_model_class, tmp_key), String).ilike(f'%{tmp_value}%'))
        query = query.order_by(self.orm_model_class.add_time.desc())
        return jsonable_encoder(LayUiTableData(
            total=query.count(),
            data_list=query.offset((page - 1) * limit).limit(limit).all()
        ).model_dump())

    def add_data_after_handle(self, po_model: Any):
        """添加数据后处理"""
        code_column = [c for c in self.orm_model_class.__table__.columns if c.name == 'code']
        if code_column:
            setattr(po_model, 'code', id_code_tools.get_code_by_id(po_model.id))
            base_crdu.update(po_model, db_code=self.db_code)

    def update_data_after_handle(self, po_model: Any):
        """更新数据后处理"""
        pass

    def delete_data_after_handle(self, po_model: Any):
        """删除数据后处理"""
        pass
