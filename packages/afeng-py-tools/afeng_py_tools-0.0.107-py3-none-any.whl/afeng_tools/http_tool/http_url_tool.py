from urllib.parse import urljoin


def join_local_url(url_info_list: list[str | int]):
    """
    合并本地的url路径
    :param url_info_list: 本地url路径列表，如：['/static','/imags/','app-test', 'test.png']
    :return: /static/image/app-test/test.png
    """
    return '/' + '/'.join([str(tmp).removeprefix('/').removesuffix('/') for tmp in url_info_list if tmp is not None])


def join_url(base_url: str, url: str | int):
    """
    合并url地址
    :param base_url: 如：https://www.afengbook.com/book/100201
    :param url: 如：/book/100202
    :return:如：https://www.afengbook.com/book/100202
    """
    return urljoin(base_url, str(url))


if __name__ == '__main__':
    test_result = join_local_url(['/static', '/image/', 'app-test', 'test.png'])
    print(test_result)
    test_url_result = join_url('https://www.afengbook.com/book/100201', '/book/100202')
    print(test_url_result)
