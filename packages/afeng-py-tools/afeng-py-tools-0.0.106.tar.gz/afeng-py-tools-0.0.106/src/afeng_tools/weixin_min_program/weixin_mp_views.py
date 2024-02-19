from afeng_tools.fastapi_tool import fastapi_router_tools
from afeng_tools.web_tool import response_tools
from afeng_tools.weixin_min_program.core import weixin_mp_service
from afeng_tools.weixin_min_program.core.weixin_mp_models import WxUserProfile, WxUserBasicInfo

router = fastapi_router_tools.create_router(prefix='/api', tags=['微信接口'])


@router.get("/wx/mp/login")
async def weixin_login(app_id: str, js_code: str):
    """
    小程序登录
    :param app_id: 小程序 App id
    :param js_code: 通过js中的wx.login()获取到的code值
    :return: token
    """
    return response_tools.create_json_response(weixin_mp_service.login_code2Session(app_id, js_code))


@router.post("/wx/mp/save_user")
async def weixin_save_user(user_profile: WxUserProfile):
    """
    小程序登录
    :param user_profile: 授权登录后获取到的用户信息
    :return: userinfo
    """
    return response_tools.create_json_response(
        weixin_mp_service.decrypt_userinfo(user_profile.app_id, user_profile.token, user_profile))


@router.post("/wx/mp/save_basic_user")
async def weixin_save_basic_user(user_basic_info: WxUserBasicInfo):
    """
    小程序登录
    :param user_basic_info: 用户基础信息
    :return: userinfo
    """
    return response_tools.create_json_response(
        weixin_mp_service.save_basic_user(user_basic_info.app_id, user_basic_info.token, user_basic_info))
