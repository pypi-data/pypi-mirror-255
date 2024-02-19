import urllib.parse


def url_encode_params(params: dict) -> str:
    """将参数进行url编码"""
    return urllib.parse.urlencode(params)


def url_encode(url: str):
    """url编码"""
    return urllib.parse.quote(url)


def url_decode(url: str):
    """url解码"""
    return urllib.parse.unquote(url)
