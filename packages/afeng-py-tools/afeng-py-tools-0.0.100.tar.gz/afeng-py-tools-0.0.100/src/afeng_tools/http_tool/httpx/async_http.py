"""异步HTTP工具"""
import httpx


class AsyncHttp:
    @classmethod
    async def get(cls, url, callback, params=None, headers=None, cookies=None, proxies=None):
        async with httpx.AsyncClient(headers=headers, cookies=cookies, proxies=proxies) as client:
            resp = await client.get(url, params=params)
            callback(resp)

    @classmethod
    async def post(cls, url, callback, data=None, headers=None, cookies=None, proxies=None):
        async with httpx.AsyncClient(headers=headers, cookies=cookies, proxies=proxies) as client:
            resp = await client.post(url, data=data)
            callback(resp)
