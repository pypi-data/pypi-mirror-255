"""
Flask 应用工具
"""
from flask import Flask

from afeng_tools.flask_tool.flask_models import UrlPatternItem


def app_set_config(app, database_uri: str):
    """设置app配置"""
    # 设置连接数据库的URI
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    # 设置每次请求结束后会自动提交数据库中的改动（不推荐使用）
    # app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    # 设置sql自动跟踪数据变化
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    # 查询时会显示原始SQL语句
    app.config['SQLALCHEMY_ECHO'] = True


def register_blueprint(app, url_pattern_list: list[UrlPatternItem]):
    """设置注册蓝图"""
    for tmp_url_pattern in url_pattern_list:
        app.register_blueprint(tmp_url_pattern.blueprint, url_prefix=tmp_url_pattern.url_prefix)


def create_app(url_pattern_list: list[UrlPatternItem]):
    """创建Flask应用"""
    app = Flask(__name__,
                static_url_path=settings.STATIC_URL_PATH,
                static_folder=settings.STATIC_FOLDER,
                template_folder=settings.TEMPLATE_FOLDER)
    # 设置app配置
    app_set_config(app)
    # 注册蓝图
    register_blueprint(app, url_pattern_list=url_pattern_list)
    # 推送应用上下文环境
    app.app_context().push()
    # 数据库db设置app
    settings.db.init_app(app)
    return app


def run_app(app):
    """启动Flask程序"""
    app.run(host=settings.HTTP_HOST, port=settings.HTTP_PORT, debug=settings.DEBUG)
