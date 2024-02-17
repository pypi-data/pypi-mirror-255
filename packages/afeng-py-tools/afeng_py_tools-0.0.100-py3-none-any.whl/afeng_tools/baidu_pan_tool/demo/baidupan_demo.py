from afeng_tools.baidu_pan_tool import baidu_pan_tools
from afeng_tools.baidu_pan_tool.baidu_pan_enum import BaidupanConfigKeyEnum
from afeng_tools.baidu_pan_tool.baidu_pan_tools import get_access_token, list_file, get_share_url
from afeng_tools.baidu_pan_tool.tools import user_tools, file_path_tools
from afeng_tools.baidu_pan_tool.tools.audio_file_tools import list_audio_category, list_audio_category, list_audio, \
    get_audio_m3u8_url
from afeng_tools.baidu_pan_tool.tools.file_download_tools import download_file, get_download_url
from afeng_tools.baidu_pan_tool.tools.file_upload_tools import upload_file, post_upload_file
from afeng_tools.baidu_pan_tool.tools.share_tools import create_share, verify_share_pwd
from afeng_tools.baidu_pan_tool.tools.video_file_tools import get_video_m3u8_url
from afeng_tools.file_tool import file_tools
from afeng_tools.baidu_pan_tool.baidu_pan_settings import get_config

def auth_demo():
    access_token = get_access_token()
    # print(user_tools.get_user_info(access_token))
    # print(user_tools.get_pan_info(access_token))
    result = list_file(access_token=access_token, dir_path='/disk/book/SEO')
    print(result.file_list)


def download_demo():
    fs_id = 36779198899466  # 428389752925140
    access_token = get_access_token()
    # download_file(access_token, fs_id, save_path='', max_size=5 * 1000 * 1000)
    down_url = get_download_url(access_token, fs_id)
    print(down_url)


def upload_demo():
    access_token = get_access_token()
    # tmp_file = r'C:\迅雷云盘\《无所畏惧：颠覆你内心的脆弱》\《无所畏惧：颠覆你内心的脆弱》.pdf'
    # upload_file(access_token, local_file=tmp_file, pan_path='pan_root_path+/tmp/test.pdf')
    # tmp_file = r'C:\迅雷云盘\《无所畏惧：颠覆你内心的脆弱》\elon.png'
    # result = upload_file(access_token, local_file=tmp_file, pan_path=pan_root_path + '/tmp/elon.png')
    tmp_file = r'C:\www\tmp\AutoToolSpace\ali_tmp_file\【公众号：zsxx_xxyg】16.电力系统一次电气设备简介(重点).ppt'
    result = upload_file(access_token, local_file=tmp_file,
                         pan_path=get_config(BaidupanConfigKeyEnum.pan_root_path) + '/learn/电气/电力系统/16.电力系统一次电气设备简介(重点).ppt')
    print(result)


def image_demo():
    pass


def audio_demo():
    access_token = get_access_token()
    result = list_audio_category(access_token=access_token)
    for tmp in result.data_list:
        list_audio_result = list_audio(access_token, mb_id=tmp.mb_id, show_meta=1)
        if list_audio_result.data_list:
            for tmp_audio in list_audio_result.data_list:
                m3u8_url, headers = get_audio_m3u8_url(access_token, tmp_audio.path)
                print(m3u8_url)


def video_demo():
    access_token = get_access_token()
    m3u8_url, headers = get_video_m3u8_url(access_token, pan_path='/电影/阿凡达.mp4')
    print(m3u8_url)


def share_demo():
    access_token = get_access_token()
    share_result = create_share(get_config(BaidupanConfigKeyEnum.app_id), access_token, fs_id_list=['36779198899466'], pwd='yyds')
    # print(share_result)
    verify_result = verify_share_pwd(get_config(BaidupanConfigKeyEnum.app_id), access_token, short_url='bqCUUYeH9HRJNxz6Y8U7nA', pwd='1234')
    print(verify_result)


def share_url_demo():
    # share_url = get_share_url('https://pan.baidu.com/s/1cmB00')
    # print(share_url)
    # share_url = get_share_url(
    #     '链接:https://pan.baidu.com/s/1C1sbTf65U-YwYCw06nHKFQ 提取码:gxlk hi，这是我用百度网盘分享的内容~复制这段内容打开「百度网盘」APP即可获取')
    # print(share_url)
    # share_url = get_share_url(
    #     '数学奥林匹克小丛书https://pan.baidu.com/share/link?uk=3443847511&shareid=82423329?pwd=yyds 提取码:gxlk hi，这')
    # print(share_url)
    line_list = file_tools.read_file_lines('share_msg.txt')
    for tmp_line in line_list:
        share_url = get_share_url(tmp_line)
        if share_url:
            print(share_url)


def baidu_pan_path_func(x):
    return '/book/暂定/' + x if x else '/book/暂定/2023年优质书籍（1-9月）'


def list_all_file_demo():
    access_token = baidu_pan_tools.get_access_token()
    exist_result = file_path_tools.list_all_by_page(access_token,
                                                    dir_path=get_config(BaidupanConfigKeyEnum.pan_root_path) + '/' + (baidu_pan_path_func('').strip('/')),
                                                    recursion=1)
    exist_file_name_list = []
    if exist_result:
        exist_file_name_list = [tmp.server_filename for tmp in exist_result.file_list]
    print(exist_file_name_list)

if __name__ == '__main__':
    # auth_demo()
    # download_demo()
    # upload_demo()
    # audio_demo()
    # video_demo()
    # share_demo()
    # share_url_demo()
    list_all_file_demo()
