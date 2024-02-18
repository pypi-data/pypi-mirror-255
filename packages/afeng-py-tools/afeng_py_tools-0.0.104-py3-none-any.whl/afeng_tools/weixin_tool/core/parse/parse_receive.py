from afeng_tools.weixin_tool.core.model.item.wx_receive_event_models import WeixinEventItem
from afeng_tools.weixin_tool.core.model.item.wx_receive_msg_models import WeixinTextMsgItem, WeixinImageMsgItem, \
    WeixinVoiceMsgItem, WeixinVideoMsgItem, WeixinLocationMsgItem, WeixinLinkMsgItem
from afeng_tools.weixin_tool.core.parse.receive_event import parse_event
from afeng_tools.weixin_tool.core.parse.receive_msg import parse_msg
from afeng_tools.weixin_tool.core.parse.receive_msg.parse_tool import parse_msg_type


def parse(openid,
          msg_bytes) -> WeixinTextMsgItem | WeixinImageMsgItem | WeixinVoiceMsgItem | WeixinVideoMsgItem | WeixinLocationMsgItem | WeixinLinkMsgItem | WeixinEventItem:
    """转换接收到的微信消息"""
    msg = msg_bytes.decode('utf-8')
    msg_type = parse_msg_type(msg)
    if msg_type == 'text':
        return parse_msg.parse_text_msg(openid, msg)
    if msg_type == 'image':
        return parse_msg.parse_image_msg(openid, msg)
    if msg_type == 'voice':
        return parse_msg.parse_voice_msg(openid, msg)
    if msg_type == 'video' or msg_type == 'shortvideo':
        return parse_msg.parse_video_msg(openid, msg)
    if msg_type == 'location':
        return parse_msg.parse_location_msg(openid, msg)
    if msg_type == 'link':
        return parse_msg.parse_link_msg(openid, msg)
    if msg_type == 'event':
        return parse_event.parse(openid, msg)
