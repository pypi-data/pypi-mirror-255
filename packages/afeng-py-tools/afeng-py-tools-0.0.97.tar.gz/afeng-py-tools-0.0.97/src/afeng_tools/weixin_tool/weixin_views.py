"""
微信公众号接口
"""
import hashlib
from typing import Callable

from fastapi import Query, Depends
from starlette.responses import PlainTextResponse, Response

from afeng_tools.fastapi_tool import fastapi_router_tools
from afeng_tools.weixin_tool import weixin_settings
from afeng_tools.weixin_tool.core import weixin_depends, weixin_reply_tool
from afeng_tools.weixin_tool.core.weixin_enums import WeixinConfigKeyEnum

router = fastapi_router_tools.create_router(prefix='/openapi', tags=['微信接口'])


@router.get("/wx")
async def check_valid_api(signature: str = Query(title='微信加密签名'),
                          timestamp: str = Query(title='时间戳'),
                          nonce: str = Query(title='随机数'),
                          echo_str: str = Query(title='随机字符串', alias='echostr')):
    if signature == hashlib.sha1(
            ''.join(sorted([weixin_settings.get_config(WeixinConfigKeyEnum.weixin_token), timestamp, nonce])).encode(
                'utf-8')).hexdigest():
        # 证明请求来自微信服务器
        return PlainTextResponse(echo_str)
    else:
        return 'Invalid request'


@router.post("/wx")
async def receive_data_api(msg_model=Depends(weixin_depends.convert_params)) -> Response:
    if msg_model:
        msg_callback = weixin_settings.get_config(WeixinConfigKeyEnum.weixin_msg_callback)
        if msg_callback and isinstance(msg_callback, Callable):
            return msg_callback(msg_model)
        else:
            return weixin_reply_tool.reply_text(msg_model, '抱歉，暂无服务！')
    return PlainTextResponse('success')

