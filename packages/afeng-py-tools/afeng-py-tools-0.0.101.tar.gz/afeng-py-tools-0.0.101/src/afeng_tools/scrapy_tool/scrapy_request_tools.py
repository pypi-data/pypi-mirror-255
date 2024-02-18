from typing import Callable, Optional, Union, List

import scrapy


def create_request(url: str, callback: Optional[Callable] = None,
                   method: str = "GET",
                   headers: Optional[dict] = None,
                   cookies: Optional[Union[dict, List[dict]]] = None,
                   body: Optional[Union[bytes, str]] = None,
                   encoding: str = "utf-8",
                   cb_kwargs: Optional[dict] = None) -> scrapy.Request:
    """
    创建request请求
    :param url: 请求地址
    :param callback: 回调
    :param method: 请求方法
    :param headers: 请求头
    :param cookies: Cookie
    :param body: 提交内容
    :param encoding: 编码
    :param cb_kwargs: 参数
    :return: scrapy.Request
    """
    return scrapy.Request(url=url,
                          method=method,
                          headers=headers,
                          cookies=cookies,
                          body=body,
                          encoding=encoding,
                          callback=callback,
                          cb_kwargs=cb_kwargs,
                          dont_filter=True)
