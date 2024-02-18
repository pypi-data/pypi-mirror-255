from afeng_tools.aliyun_pan_tool.aliyun_pan_share_tools import get_share_info_by_link, list_share_root_files
from afeng_tools.aliyun_pan_tool.aliyun_pan_tools import get_user_info, get_ali_api, get_file_info, list_file, list_path


def user_info_demo():
    ali_api = get_ali_api()
    user_info = get_user_info(ali_api)
    print(user_info.user_name, user_info.nick_name, user_info.phone)


def list_root_file_demo():
    ali_api = get_ali_api()
    file_list = list_file(ali_api)
    for tmp_file in file_list:
        # 打印文件信息
        # 文件id，如：'63b8e37d08f61f64808b4dfdba2c1119ed140464'
        print(tmp_file.file_id)
        # 文件名，如：'电气'
        print(tmp_file.name)
        # 父id，如：root
        print(tmp_file.parent_file_id)
        # 文件类型 folder:文件夹  file：文件
        print(tmp_file.type)
        # 创建时间,如：'2023-01-07T03:14:05.721Z'
        print(tmp_file.created_at)
        # 修改时间,如：'2023-01-07T03:14:05.721Z'
        print(tmp_file.updated_at)


def share_url_demo():
    ali_api = get_ali_api()
    share_msg = '@夏因平典 数学奥林匹克小丛书 https://www.aliyundrive.com/s/Fu8CA5JoRQy/folder/6356a27c044a680bec9b49a6a6711536ef44c01c'
    result = get_share_info_by_link(ali_api, share_msg)
    share_id = result.share_id
    file_list = list_share_root_files(ali_api, share_id)
    for tmp_file in file_list:
        # 打印文件信息
        # 文件id，如：'63b8e37d08f61f64808b4dfdba2c1119ed140464'
        print(tmp_file.file_id)
        # 文件名，如：'电气'
        print(tmp_file.name)
        # 父id，如：root
        print(tmp_file.parent_file_id)
        # 文件类型 folder:文件夹  file：文件
        print(tmp_file.type)
        # 创建时间,如：'2023-01-07T03:14:05.721Z'
        print(tmp_file.created_at)
        # 修改时间,如：'2023-01-07T03:14:05.721Z'
        print(tmp_file.updated_at)


def list_file_demo():
    ali_api = get_ali_api()
    # tmp_file = get_file_info(ali_api, '电气')
    # tmp_file = get_file_info(ali_api, 'Python/Python中文书籍汇总/机器学习实战.pdf')
    tmp_file = list_path(ali_api, '电气')
    print(tmp_file)


if __name__ == '__main__':
    # user_info_demo()
    # list_file_demo()
    # share_url_demo()
    list_file_demo()
