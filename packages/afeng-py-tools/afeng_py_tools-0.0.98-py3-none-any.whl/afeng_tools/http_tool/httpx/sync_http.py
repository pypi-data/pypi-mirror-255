"""同步http工具"""
import httpx


class SyncHttp:
    @classmethod
    def get(cls, url, params=None, headers=None, cookies=None, proxies=None):
        return httpx.get(url, params=params, headers=headers, cookies=cookies, proxies=proxies)

    @classmethod
    def post(cls, url, data=None, headers=None, cookies=None, proxies=None):
        return httpx.post(url=url, data=data, headers=headers, cookies=cookies, proxies=proxies)

    @classmethod
    def get_cookie(cls, url, params=None, headers=None, cookies=None, proxies=None):
        resp = cls.get(url, params=params, headers=headers, cookies=cookies, proxies=proxies)
        return resp.cookies
