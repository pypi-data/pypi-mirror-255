import os


from afeng_tools.fastapi_tool import fastapi_app_tools

from afeng_tools.fastapi_tool.fastapi_router_tools import auto_load_routers
from web.admin_router import admin_router_list

# url路径配置列表
router_list = auto_load_routers(os.path.dirname(__file__))
# 添加管理路径
router_list.extend(admin_router_list)
# 创建app
app = fastapi_app_tools.create_app(router_list)
