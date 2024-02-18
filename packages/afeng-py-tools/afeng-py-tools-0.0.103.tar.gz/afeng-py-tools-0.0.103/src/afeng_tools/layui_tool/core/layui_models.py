from typing import Literal, Optional, Any

from pydantic import BaseModel


class LayUiFormCascaderItem(BaseModel):
    """layui cascader 仿element-ui级联选择器: https://gitee.com/yixiacoco/lay_cascader """
    label: str
    value: str
    disabled: bool = False
    children: Optional[list['LayUiFormCascaderItem']] = None


class LayUiFormItem(BaseModel):
    """表单项"""
    title: str
    type: Literal['hidden', 'array',
    'text', 'number', 'email', 'radio', 'cascader', 'checkbox', 'switch', 'select', 'password', 'textarea', 'file'] = 'text'
    name: str
    autocomplete: Literal['off', 'on'] = 'off'
    default: Optional[str | int | Any] = None
    readonly: bool = False
    required: bool = False
    required_text: Optional[str] = None
    # 同时支持多条规则的验证("验证A|验证B"), required（必填项）phone（手机号） email（邮箱）url（网址）number（数字）date（日期）identity（身份证）自定义值
    verify: Optional[Literal['required', 'phone', 'email', 'url', 'number', 'date', 'identity'] | str] = None
    # 用于定义异常提示层模式。: tips（吸附层） alert（对话框） msg（默认）
    verify_type: Literal['tips', 'alert', 'msg'] = 'tips'
    placeholder: Optional[str] = None
    tip: Optional[str] = None
    # 当type为radio时， 下面 [(value, title, checked)]
    radio_list: Optional[list[tuple[str, str, bool]]] = None
    # 当type为cascader时， 下面 json.dumps([LayUiFormCascaderItem.model_dump()], ensure_ascii=False)
    cascader_list: Optional[str] = None
    # 当type为checkbox时， 下面 [(value, title, checked, disabled)]
    checkbox_list: Optional[list[tuple[str, str, bool, bool]]] = None
    # 当type为switch时， 下面 (value(0/1), title(开启|关闭 / ON|OFF), checked, disabled)
    switch_item: Optional[tuple[str, str, bool, bool]] = None
    # 当type为select时， 下面 [(value, title, selected, disabled)]
    select_list: Optional[list[tuple[str, str, bool, bool]]] = None
    # 当type为file时
    file_upload_url: Optional[str] = None
    file_upload_title: Optional[str] = '上传文件'
    # 上传属性（上传时需要的额外表单参数）
    file_upload_params: Optional[list[str]] = None
    # 上传后的处理操作
    file_upload_after_handle_js: Optional[str] = None


class LayUiTableCol(BaseModel):
    """表格列"""
    field: str
    title: str
    width: Optional[int] = None
    min_width: Optional[int] = None
    sort: bool = False
    is_enum: bool = False


class LayUiTableData(BaseModel):
    """表格数据"""
    code: int = 0
    message: Optional[str] = None
    total: int
    data_list: list


class LayUiTableActionItem(BaseModel):
    """表格操作"""
    # 标题
    title: str
    url: str
    # 完成后是否刷新表格页面
    reload: bool = False
    # 参数连接字符
    param_link_char: str = '?'
    param_name: str = 'id_value'
    param_field: str = 'id'
    target: Literal['_self', '_parent', '_blank'] = '_self'


class LayUiFormStep(BaseModel):
    code: str
    # 步骤标题
    title: str
    # 步骤表单
    form_item_list: list[LayUiFormItem]
    # 提交链接
    submit_url: str
    after_handle_js: Optional[str] = None
