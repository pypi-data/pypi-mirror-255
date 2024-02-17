"""
百度网盘授权工具
- pip install pytest-playwright -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
"""
from datetime import datetime
from typing import Literal

from playwright.sync_api import Page

import openapi_client
from openapi_client.api.auth_api import AuthApi
from afeng_tools.baidu_pan_tool.core.baidu_pan_api_tools import filter_login_qrcode_api, delete_login_qrcode_image
from afeng_tools.baidu_pan_tool.core.baidu_pan_decorator_tools import auto_auth_api
from afeng_tools.baidu_pan_tool.core.baidu_pan_models import TokenInfo, GrantTokenInfo, DeviceCodeInfo
from afeng_tools.http_tool import http_params_tools
from afeng_tools.log_tool.loguru_tools import get_logger, log_error
from afeng_tools.playwright_tool.decorator.playwright_decorators import auto_input
from afeng_tools.math_tool.random_tools import random_state

logger = get_logger()


@auto_input(headless=False)
def get_authorization_code(app_id: str, app_key: str,
                           redirect_uri: str = 'oob',
                           display: Literal['page', 'popup', 'dialog', 'mobile', 'tv', 'pad'] | str = 'page',
                           qrcode: int = 1, force_login: int = 0, web_page: Page = None) -> str:
    """
    获取授权码Code
    :param app_id: AppID
    :param app_key: 应用的AppKey。
    :param redirect_uri: 授权后要回调的地址URL
            可传 redirect_uri=oob,回调后会返回一个平台提供默认回调地址：http://openapi.baidu.com/oauth/2.0/login_success。
    :param display:
            page: 全屏形式的授权页面(默认)，适用于 web 应用。
            popup: 弹框形式的授权页面，适用于桌面软件应用和 web 应用
            dialog: 浮层形式的授权页面，只能用于站内 web 应用
            mobile: Iphone/Android 等智能移动终端上用的授权页面，适用于 Iphone/Android 等智能移动终端上的应用
            tv: 电视等超大显示屏使用的授权页面
            pad: 适配 IPad/Android 等智能平板电脑使用的授权页面
    :param qrcode: 	让用户通过扫二维码的方式登录百度账号时，可传递 “qrcode=1”
    :param force_login: 当需要加载登录页时强制用户用户输入用户名和密码，不会从 Cookies 中读取百度用户的登录状态时，传递 “force_login=1”
    :param web_page: playwright中访问浏览器页面，自动注入
    :return: 获取到的授权码 code 有效期 10 分钟，且仅一次有效。
    """
    params = {
        'response_type': 'code',
        'client_id': app_key,
        'redirect_uri': redirect_uri,
        'scope': 'basic,netdisk',
        'device_id': app_id,
        'state': random_state(),
        'display': display,
        'qrcode': qrcode,
        'force_login': force_login
    }
    auth_url = 'http://openapi.baidu.com/oauth/2.0/authorize?' + http_params_tools.url_encode_params(params)
    logger.info(f'[BaiduPan]登录认证url：{auth_url}')
    web_page.on('response', lambda response: filter_login_qrcode_api(response))
    web_page.goto(auth_url)
    web_page.locator('#d_clip_button', has_text='复制授权码').click()
    delete_login_qrcode_image()
    return web_page.locator('#Verifier').input_value()


@auto_auth_api
def get_token_authorization_code(auth_code: str, app_key: str, secret_key: str,
                                 redirect_uri: str = 'oob', api_instance: AuthApi = None) -> TokenInfo:
    """
    授权码模式: 用户授权后生成授权码 Code，开发者应用通过 Code 换取 Access Token。
    :param auth_code: 授权码Code
    :param app_key: 应用的AppKey
    :param secret_key: 应用的SecretKey
    :param redirect_uri: 应用设置的授权回调地址
    :param api_instance: 自动注入AuthApi
    :return: Access Token 有效期30天，过期后支持刷新。
    """
    try:
        api_response = api_instance.oauth_token_code2token(auth_code, app_key, secret_key, redirect_uri)
        return TokenInfo(
            access_token=api_response['access_token'],
            expires_in=api_response['expires_in'],
            refresh_token=api_response['refresh_token'],
            scope=api_response['scope'],
            token_time=datetime.now()
        )
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling AuthApi->oauth_token_code2token", e)


@auto_input(headless=False)
def get_token_implicit_grant(app_key: str,
                             display: Literal['page', 'popup', 'dialog', 'mobile', 'tv', 'pad'] | str = 'page',
                             redirect_uri: str = 'oob', web_page: Page = None) -> GrantTokenInfo:
    """
    简化模式: 无需通过 Code 换取 Access Token，直接获取 Access Token。
    :return: Access Token 有效期30天，过期后不支持刷新, 用户需重新登录授权。
    """
    params = {
        'response_type': 'token',
        'client_id': app_key,
        'redirect_uri': redirect_uri,
        'scope': 'basic,netdisk',
        'display': display,
        'state': random_state(),
    }
    auth_url = 'http://openapi.baidu.com/oauth/2.0/authorize?' + http_params_tools.url_encode_params(params)
    logger.info(f'[BaiduPan]登录认证url：{auth_url}')
    web_page.goto(auth_url)
    web_page.wait_for_url('http://openapi.baidu.com/oauth/2.0/login_success')
    print(web_page.url)
    auth_str = web_page.url.rsplit('#', 1)[1]
    auth_info_list = auth_str.split('&')
    grant_token_info = GrantTokenInfo()
    for tmp in auth_info_list:
        tmp_auth_list = tmp.split('=')
        grant_token_info.__setattr__(tmp_auth_list[0], tmp_auth_list[1])
    return grant_token_info


@auto_auth_api
def get_device_code(app_key: str, api_instance: AuthApi = None) -> DeviceCodeInfo:
    """
    获取设备码 device_code和user_code
    :param app_key: 应用的AppKey
    :param api_instance: 自动注入的 AuthApi
    :return: Device Code只能使用一次
    """
    scope = "basic,netdisk"
    try:
        api_response = api_instance.oauth_token_device_code(client_id=app_key, scope=scope)
        return DeviceCodeInfo(
            device_code=api_response['device_code'],
            user_code=api_response['user_code'],
            verification_url=api_response['verification_url'],
            qrcode_url=api_response['qrcode_url'],
            expires_in=api_response['expires_in'],
            interval=api_response['interval']
        )
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling AuthApi->oauth_token_device_code", e)


@auto_auth_api
def get_token_device_code(device_code: str, app_key: str, secret_key: str, api_instance: AuthApi = None):
    """
    设备码模式: 获取设备码，用户授权后，开发者应用通过设备码换取 Access Token。
        轮询此接口每两次请求时间间隔应大于5秒。
    :param device_code: 获取设备码
    :param app_key: 应用的AppKey
    :param secret_key: 应用的SecretKey
    :param api_instance: 自动注入的 AuthApi
    :return: Access Token过期后支持刷新。
    """
    try:
        api_response = api_instance.oauth_token_device_token(code=device_code,
                                                             client_id=app_key, client_secret=secret_key)
        return TokenInfo(
            access_token=api_response['access_token'],
            expires_in=api_response['expires_in'],
            refresh_token=api_response['refresh_token'],
            scope=api_response['scope'],
            token_time=datetime.now()
        )
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling AuthApi->oauth_token_device_token", e)


@auto_auth_api
def refresh_token(refresh_token_value: str, app_key: str,
                  secret_key: str, api_instance: AuthApi = None) -> TokenInfo:
    """
    刷新Token：
    :param refresh_token_value: 获取 Access Token时返回的 refresh_token 值， refresh_token 只支持使用一次， 使用后失效
    :param app_key: 应用的AppKey
    :param secret_key: 应用的SecretKey
    :param api_instance: 自动注入的 AuthApi
    :return: 刷新后的 Access Token 有效期仍为 30 天
    """
    try:
        api_response = api_instance.oauth_token_refresh_token(refresh_token_value, app_key, secret_key)
        return TokenInfo(**{
            'access_token': api_response['access_token'],
            'expires_in': api_response['expires_in'],
            'refresh_token': api_response['refresh_token'],
            'scope': api_response['scope'],
            'token_time': datetime.now()
        })
    except openapi_client.ApiException as e:
        log_error(logger, "[BaiduPan]Exception when calling AuthApi->oauth_token_refresh_token", e)

