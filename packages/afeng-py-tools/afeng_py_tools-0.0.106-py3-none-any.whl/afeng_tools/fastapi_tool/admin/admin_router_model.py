from typing import Type

from afeng_tools.fastapi_tool.admin.admin_views_template import AdminViewsTemplate
from afeng_tools.layui_tool.core.layui_models import LayUiFormItem


class AdminRouterModel:
    """管理路由模型"""

    def __init__(self, module_code: str, tag_list: list[str], orm_model_class: Type, search_form_item_list: list[LayUiFormItem],
                 admin_views_template: AdminViewsTemplate = None,
                 admin_views_template_class: Type[AdminViewsTemplate] = None, db_code='default'):
        self.module_code = module_code
        self.tag_list = tag_list
        self.orm_model_class = orm_model_class
        self.search_form_item_list = search_form_item_list
        if admin_views_template is None:
            if admin_views_template_class:
                self.admin_views_template = admin_views_template_class(module_code=self.module_code,
                                                                       orm_model_class=self.orm_model_class,
                                                                       search_form_item_list=self.search_form_item_list,
                                                                       db_code=db_code)
            else:
                self.admin_views_template = AdminViewsTemplate(module_code=self.module_code,
                                                               orm_model_class=self.orm_model_class,
                                                               search_form_item_list=self.search_form_item_list,
                                                               db_code=db_code)
        else:
            self.admin_views_template = admin_views_template
