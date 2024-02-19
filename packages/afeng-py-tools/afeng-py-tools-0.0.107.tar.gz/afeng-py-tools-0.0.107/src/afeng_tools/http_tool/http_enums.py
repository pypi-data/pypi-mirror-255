"""
http枚举
"""
from enum import Enum


class HttpMethodEnum(Enum):
    post = 'POST'
    get = 'GET'
    put = 'PUT'
    delete = 'DELETE'
    head = 'HEAD'
    options = 'OPTIONS'
    patch = 'PATCH'


class HttpContentTypeEnum(Enum):
    form_urlencoded = 'application/x-www-form-urlencoded;charset=utf-8'
    form_data = 'application/x-www-form-urlencoded, multipart/form-data'
    json = 'application/json;charset=utf-8'
    xml = 'application/xml'
    text = 'text/plain'

