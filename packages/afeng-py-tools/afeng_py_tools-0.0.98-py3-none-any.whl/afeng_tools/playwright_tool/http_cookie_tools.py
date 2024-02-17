import json

from playwright.sync_api import Page
from requests.cookies import RequestsCookieJar

from afeng_tools.serialization_tool import pickle_tools


def save_cookies(page: Page, auth_cookie_file: str):
    """保存Cookie"""
    cookie_list = page.context.cookies()
    cookie_str = json.dumps(cookie_list)
    with open(auth_cookie_file, 'wb') as cookie_file:
        cookie_file.write(cookie_str.encode('utf-8'))


def set_cookies(page: Page, auth_cookie_file: str):
    """设置Cookie"""
    with open(auth_cookie_file, 'rb') as cookie_file:
        cookie_str = cookie_file.read()
    cookie_list = json.loads(cookie_str)
    page.context.add_cookies(cookie_list)
    page.reload()


def get_cookies(auth_cookie_file: str) -> dict:
    """获取Cookie"""
    with open(auth_cookie_file, 'rb') as cookie_file:
        cookie_str = cookie_file.read()
    cookie_list = json.loads(cookie_str)
    cookie_dict = {}
    for tmp_cookie in cookie_list:
        cookie_dict[tmp_cookie['name']] = tmp_cookie['value']
    return cookie_dict


def save_cookie_jar(cookies: RequestsCookieJar, auth_cookie_file: str):
    """保存cookie"""
    pickle_tools.save_to_file([cookies], auth_cookie_file)


def get_cookie_jar(auth_cookie_file: str) -> RequestsCookieJar:
    """获取cookie"""
    return pickle_tools.parse_to_obj(auth_cookie_file)[0]


if __name__ == '__main__':
    cookies = RequestsCookieJar()
    cookies.set('LTWSESSID', '1ni1rd7u6agc468ogjubprtdda')
    cookies.set('SERVERID', '4cb8c33eaf77df5ec4c43a1d17a68293|1696528114|1696528114')
    cookies.set('cklogin', 'e58f53bd6e40770a3efdeb203825b879226e659ce9afdcec559f59f11d28dfada')
    cookies.set('mmopen', '2FpxGzl2aG2hnvCSoibR7cFralsdUpMG1nqViaSM9rF0HXoS50tGrRIMABlnvLJXialiaDwFsYeqcia6MpPyHhIicul7bg')
    save_cookie_jar(cookies, 'temp_cookie.txt')
    cookies = get_cookie_jar('temp_cookie.txt')
    print(cookies)