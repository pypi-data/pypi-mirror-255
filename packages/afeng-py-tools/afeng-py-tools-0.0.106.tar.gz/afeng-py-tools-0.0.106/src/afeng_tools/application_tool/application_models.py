from typing import Optional, Any, Callable

from pydantic import BaseModel, Field, field_validator
from starlette.requests import Request


class AppInfo(BaseModel):
    # 编码，如：'afeng_book'
    code: str
    # 标题，如：阿锋书屋
    title: str
    # 数据库编码(默认是：code+‘_db’)，如：'afeng_book_db'
    db_code: Optional[str] = None
    # 数据库url，如：postgresql://root:123456@127.0.0.1:5432/afeng-book-db
    db_url: Optional[str] = None
    # 路径前缀，如：'/book'
    prefix: Optional[str] = None
    # 是否全是json接口
    is_json_api: Optional[bool] = None
    # 副标题
    sub_title: Optional[str] = None
    # 介绍
    description: Optional[str] = None
    # 关键字
    keywords: Optional[list[str]] = None
    # 域信息，如：https://www.afenghome.com
    origin: Optional[str] = None
    # 备案信息，如：'京ICP备2023032898号-1'
    icp_record_info: Optional[str] = None
    # 公安备案号，如：'xxxx'
    police_record_info: Optional[str] = None
    # 联系信息，如：'QQ: 1640125562'
    contact_info: Optional[str] = None
    # 联系QQ，如：'1640125562'
    contact_qq: Optional[str] = None
    # 联系邮箱，如：'afengbook@aliyun.com'
    contact_email: Optional[str] = None
    # app根路径：os.path.dirname(__file__)
    root_path: Optional[str] = None
    # app的web路径：os.path.join(root_path, 'web')
    web_path: Optional[str] = None
    # 错误404创建context_data的函数，参数：(message: str, is_mobile: bool = False)
    error404_callback_func: Optional[Callable[[str, bool], dict]] = None
    # 错误500创建context_data的函数，参数：(message: str, is_mobile: bool = False)
    error500_callback_func: Optional[Callable[[str, bool], dict]] = None
    # 500异常后后台工作函数，如发送邮件, async def send_email(request: Request, exception: Exception, traceback_msg: str)
    error500_background_work_func: Optional[Callable[[Request, Exception, str], None]] = None
    # 错误501创建context_data的函数，参数：(message: str, is_mobile: bool = False)
    error501_callback_func: Optional[Callable[[str, bool], dict]] = None

    @field_validator('db_code')
    @classmethod
    def set_db_code(cls, v: Any):
        if not v:
            return cls.code + '_db'
        return v


class BaiduInfo(BaseModel):
    app_id: str
    app_key: str
    app_secret_key: str
    sign_key: Optional[str] = None


class WeixinInfo(BaseModel):
    app_id: str
    app_secret_key: str
    token: Optional[str] = None
    encoding_aes_key: Optional[str] = None
    token_file: Optional[str] = None
    msg_callback: Optional[Callable[[Any], None]] = None


class EmailInfo(BaseModel):
    # 昵称
    nickname: str
    # 登录邮箱
    login_email: str
    # 密码
    password: Optional[str] = None
