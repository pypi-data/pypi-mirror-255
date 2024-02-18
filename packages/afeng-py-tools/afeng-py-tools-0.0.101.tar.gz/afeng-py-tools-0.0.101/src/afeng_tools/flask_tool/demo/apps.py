# 创建Flask应用
from util.flask import flask_app_tools
from web.urls import url_pattern_list

app = flask_app_tools.create_app(url_pattern_list)


def run_app():
    """运行app"""
    flask_app_tools.run_app(app)


if __name__ == '__main__':
    run_app()
