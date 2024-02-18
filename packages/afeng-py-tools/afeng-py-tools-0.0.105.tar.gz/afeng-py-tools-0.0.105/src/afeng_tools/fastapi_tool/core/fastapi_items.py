from typing import Callable, Optional

from pydantic import BaseModel
from starlette.requests import Request


class FastapiConfigItem(BaseModel):
    is_json_api: Optional[bool] = None
    # 错误404创建context_data的函数，参数：(message: str, is_mobile: bool = False)
    error404_context_data_func: Optional[Callable[[str, bool], dict]] = None
    # 错误500创建context_data的函数，参数：(message: str, is_mobile: bool = False)
    error500_context_data_func: Optional[Callable[[str, bool], dict]] = None
    # 500异常后后台工作函数，如发送邮件, async def send_email(request: Request, exception: Exception, traceback_msg: str)
    error500_background_work_func: Optional[Callable[[Request, Exception, str], None]] = None
    # 错误501创建context_data的函数，参数：(message: str, is_mobile: bool = False)
    error501_context_data_func: Optional[Callable[[str, bool], dict]] = None
