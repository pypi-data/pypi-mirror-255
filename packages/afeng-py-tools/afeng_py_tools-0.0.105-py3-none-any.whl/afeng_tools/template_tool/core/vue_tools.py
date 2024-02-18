"""
vue工具： pip install vbuild -i https://pypi.tuna.tsinghua.edu.cn/simple/ -U
- https://pypi.org/project/vbuild/
"""
import vbuild


def render_vue(vue_file: str | tuple[str]):
    """
    渲染vue
    :param vue_file: mycompo.vue 或   vues/*.vue  或  ["c1.vue", "c2.vue"]
    :return: (html, script, style)
    """

    if isinstance(vue_file, list):
        vue_render = vbuild.render(*vue_file)
    else:
        vue_render = vbuild.render(vue_file)
    return vue_render.html, vue_render.script, vue_render.style


def replace_html_template(html_template_file: str, vue_file: str, vue_template_tag: str = '<!-- HERE -->'):
    """
    替换html模板中的内容
    :param html_template_file: html模板文件
    :param vue_file: mycompo.vue  或   vues/*.vue
    :param vue_template_tag: vue模板标记
    :return: 替换模板内容后的html内容
    """
    with open(html_template_file, encoding='utf-8') as fid:
        template_content = fid.read()
    vue_render = vbuild.render(vue_file)
    return template_content.replace(vue_template_tag, str(vue_render))
