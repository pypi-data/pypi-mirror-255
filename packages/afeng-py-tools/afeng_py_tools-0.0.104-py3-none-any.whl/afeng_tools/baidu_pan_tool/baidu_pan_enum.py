"""
百度网盘枚举
"""
from enum import Enum


class BaidupanConfigKeyEnum(Enum):
    app_name = 'app_name'
    app_id = 'app_id'
    app_key = 'app_key'
    secret_key = 'secret_key'
    sign_key = 'sign_key'
    redirect_url = 'redirect_url'
    auth_qrcode_image = 'auth_qrcode_image'
    token_file = 'token_file'
    pan_root_path = 'pan_root_path'

