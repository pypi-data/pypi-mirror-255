import logging
import os.path
import time
import traceback

from afeng_tools.file_tool import file_tools
from afeng_tools.template_tool import template_tools


def init_file_info_dict(vue_path: str, relative_file_list: list[str]) -> dict[str, float]:
    """初始化文件信息字典"""
    result_file_info_dict = {}
    for tmp_relative_file in relative_file_list:
        if tmp_relative_file.endswith('.vue'):
            result_file_info_dict[tmp_relative_file] = os.stat(os.path.join(vue_path, tmp_relative_file)).st_mtime
    return result_file_info_dict


def list_update_file(vue_path: str, old_file_info_dict: dict[str, float]):
    """列出更新文件"""
    relative_file_list, absolute_file_list = file_tools.list_files(vue_path, recursion=True,
                                                                   include_folder=False)
    result_file_list = []
    for tmp_relative_file in relative_file_list:
        if tmp_relative_file.endswith('.vue') and old_file_info_dict.get(tmp_relative_file):
            if os.stat(os.path.join(vue_path, tmp_relative_file)).st_mtime > old_file_info_dict[tmp_relative_file]:
                result_file_list.append(tmp_relative_file)
    return result_file_list


def get_vue_file_info_list(vue_path: str) -> dict[str, float]:
    """获取vue文件更新时间列表"""
    relative_file_list, _ = file_tools.list_files(vue_path, recursion=True, include_folder=False)
    return init_file_info_dict(vue_path, relative_file_list)


def render_vue_to_template(vue_file, template_file, template_root_path: str):
    """渲染 vue 模板为html模板"""
    html_code, js_code, css_code = template_tools.render(vue_file, template_root_path=template_root_path)
    template_content = css_code + html_code + js_code
    with open(template_file, 'w', encoding='utf-8') as tmp_file:
        tmp_file.write(template_content)
    return template_content


def render_vues_to_templates(vue_path: str, html_path: str, old_file_info_dict: dict[str, float],
                             template_root_path: str):
    """渲染 路径中的vue 模板为html模板"""
    vue_file_list = list_update_file(vue_path, old_file_info_dict)
    result_flag = False
    for tmp_vue_file in vue_file_list:
        tmp_html_file_name = tmp_vue_file.rsplit('.', maxsplit=1)[0] + '.html'
        tmp_html_file = os.path.join(os.path.join(html_path, tmp_html_file_name))
        os.makedirs(os.path.dirname(tmp_html_file), exist_ok=True)
        try:
            render_vue_to_template(os.path.join(vue_path, tmp_vue_file), tmp_html_file,
                                   template_root_path=template_root_path)
            print(f'成功渲染[{tmp_vue_file}]为[{tmp_html_file}]')
        except Exception as ex:
            logging.error(f'失败渲染[{tmp_vue_file}]为[{tmp_html_file}]:{ex}\n {traceback.format_exc()}')
        result_flag = True
    return result_flag


def refresh_render(vue_path: str, html_path: str, template_root_path: str):
    """刷新渲染"""
    relative_file_list, _ = file_tools.list_files(vue_path, recursion=True, include_folder=False)
    for tmp_relative_file in relative_file_list:
        if tmp_relative_file.endswith('.vue') and not os.path.exists(os.path.join(html_path, tmp_relative_file).removesuffix('.vue') + '.html'):
            tmp_vue_file = os.path.join(vue_path, tmp_relative_file)
            tmp_html_file = os.path.join(html_path, tmp_relative_file).removesuffix('.vue') + '.html'
            os.makedirs(os.path.dirname(tmp_html_file), exist_ok=True)
            try:
                render_vue_to_template(tmp_vue_file,
                                       tmp_html_file,
                                       template_root_path=template_root_path)
                print(f'成功渲染[{tmp_vue_file}]为[{tmp_html_file}]')
            except Exception as ex:
                logging.error(f'失败渲染[{tmp_vue_file}]为[{tmp_html_file}]:{ex}\n {traceback.format_exc()}')


def run_auto_render(vue_path: str, html_path: str, template_root_path: str):
    """运行自动渲染"""
    file_info_dict = get_vue_file_info_list(vue_path)
    print('启动自动渲染程序...')
    while True:
        render_flag = render_vues_to_templates(vue_path, html_path, file_info_dict,
                                               template_root_path=template_root_path)
        if render_flag:
            file_info_dict.update(get_vue_file_info_list(vue_path))
        else:
            new_file_info_dict = get_vue_file_info_list(vue_path)
            new_file_info_dict.update(file_info_dict)
            file_info_dict = new_file_info_dict
        refresh_render(vue_path, html_path, template_root_path)
        time.sleep(1)


if __name__ == '__main__':
    # pc端
    vue_template_path = r'C:\pythonwork\afeng-bookroom\resource\template\pc\component'
    html_template_path = r'C:\pythonwork\afeng-bookroom\resource\template\pc\tmp'
    # 手机端
    mobile_vue_template_path = r'C:\pythonwork\afeng-bookroom\resource\template\mobile\component'
    mobile_html_template_path = r'C:\pythonwork\afeng-bookroom\resource\template\mobile\tmp'
    template_roo = r'C:\pythonwork\afeng-bookroom\resource\template'
    # run_auto_render(vue_template_path, html_template_path, template_root_path=template_roo)
    run_auto_render(mobile_vue_template_path, mobile_html_template_path, template_root_path=template_roo)
