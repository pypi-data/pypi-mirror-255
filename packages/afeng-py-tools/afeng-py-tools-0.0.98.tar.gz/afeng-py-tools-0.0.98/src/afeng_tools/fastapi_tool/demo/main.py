import uvicorn
from config import settings
from afeng_tools.application_tool import settings_tools
from afeng_tools.application_tool.settings_enum import SettingsKeyEnum
from web.apps import app

if __name__ == '__main__':
    http_host = settings_tools.get_config('server.host')
    http_port = settings_tools.get_config('server.port')
    # 实现类似命令的效果：uvicorn main:app --reload  --host 0.0.0.0
    if settings_tools.get_config(SettingsKeyEnum.app_is_debug):
        uvicorn.run('main:app', host=http_host, port=http_port, log_level="debug", reload=True, workers=4)
    else:
        uvicorn.run('main:app', host=http_host, port=http_port, log_level="info", workers=8)
