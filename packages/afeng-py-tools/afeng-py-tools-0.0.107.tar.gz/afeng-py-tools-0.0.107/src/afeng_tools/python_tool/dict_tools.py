
def tree_get_value(data_dict: dict, key_list: list[str]):
    """
    递归获取字典的值
    :param data_dict:数据字典，如:  {'app' :{'log': {'error': {'file': 'test.log'}}}}
    :param key_list: 层级的键列表，如：['app', 'log', 'error', 'file']
    :return: 获取到的值, 如：'test.log'
    """
    if data_dict is None:
        return None
    if len(key_list) > 1:
        return tree_get_value(data_dict.get(key_list[0]), key_list[1:])
    else:
        return data_dict.get(key_list[0])


def tree_set_value(data_dict: dict, key_list: list[str], value):
    """
    递归设置字典的值
    :param data_dict: 数据子弹
    :param key_list: 键值列表， [app, static, path]
    :param value: 值
    :return:
    """
    if not data_dict.get(key_list[0]):
        data_dict[key_list[0]] = dict()
    if len(key_list) > 1:
        tree_set_value(data_dict[key_list[0]], key_list[1:], value)
    else:
        data_dict[key_list[0]] = value


def format_config_dict(config_dict: dict):
    """
    格式化配置字典
    :param config_dict:
        如：{
            'app.port': 18080,
            'app.log.info.file': 'log_error.log',
            'app.log.error.file': 'log_error.log',
            'app.static.url': '/static',
            'app.static.path': '/data/www/static',
        }
    :return: 格式化后的字典
            {
                "app": {
                    "port": 18080,
                    "log": {
                        "info": {
                            "file": "log_error.log"
                        },
                        "error": {
                            "file": "log_error.log"
                        }
                    },
                    "static": {
                        "url": "/static",
                        "path": "/data/www/static"
                    }
                },
                "app.port": 18080,
                "app.log.info.file": "log_error.log",
                "app.log.error.file": "log_error.log",
                "app.static.url": "/static",
                "app.static.path": "/data/www/static"
            }
    """
    result_data_dict = dict()
    for tmp_key, tmp_value in config_dict.items():
        if '.' in tmp_key:
            tmp_key_list = tmp_key.split('.')
            tree_set_value(result_data_dict, tmp_key_list, tmp_value)
        result_data_dict[tmp_key] = tmp_value
    return result_data_dict

