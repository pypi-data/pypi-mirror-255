from afeng_tools.aliyun_pan_tool.aliyun_pan_share_tools import get_share_info_by_link, list_share_root_files, get_share_token
from afeng_tools.aliyun_pan_tool.aliyun_pan_tools import get_ali_api


def list_share_root_files_demo():
    ali_api = get_ali_api()
    result = get_share_info_by_link(ali_api, share_msg='https://www.aliyundrive.com/s/1GmJaHi5aMk/folder/625abafa180f8e98698c4ce49c9b04809d3202fc')
    print(result)
    share_token = get_share_token(ali_api, result.share_id)
    root_file_list = list_share_root_files(ali_api, share_token)
    for tmp_file in root_file_list:
        print(tmp_file)

def download_share_file_demo():
    pass

if __name__ == '__main__':
    list_share_root_files_demo()