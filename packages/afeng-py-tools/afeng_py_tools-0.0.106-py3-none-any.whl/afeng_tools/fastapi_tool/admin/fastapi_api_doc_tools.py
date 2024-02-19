from typing import Optional

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse

from afeng_tools.application_tool import settings_tools
from afeng_tools.application_tool.settings_enum import SettingsKeyEnum


def run_api_doc(app: FastAPI, openapi_url: Optional[str] = "/admin/openapi.json",
                docs_url: Optional[str] = "/admin/docs",
                redoc_url: Optional[str] = "/admin/redoc",
                swagger_ui_oauth2_redirect_url: Optional[str] = "/admin/oauth2-redirect"):
    app_config = {
        'title': settings_tools.get_config(SettingsKeyEnum.app_name),
        'openapi_url': openapi_url,
        'oauth2_redirect_url': swagger_ui_oauth2_redirect_url,
        'swagger_ui_init_oauth': None,
        'swagger_ui_parameters': None,
    }

    # openapi
    async def doc_openapi(req: Request) -> JSONResponse:
        return JSONResponse(app.openapi())
    app.add_route(openapi_url, doc_openapi, include_in_schema=False)

    # Swagger UI
    async def swagger_ui_html(req: Request) -> HTMLResponse:
        return get_swagger_ui_html(
            openapi_url=app_config['openapi_url'],
            title=str(app_config['title']) + " - Swagger页面",
            oauth2_redirect_url=app_config['oauth2_redirect_url'],
            init_oauth=app_config['swagger_ui_init_oauth'],
            swagger_ui_parameters=app_config['swagger_ui_parameters'],
            swagger_js_url="https://cdn.staticfile.org/swagger-ui/5.9.0/swagger-ui-bundle.min.js",
            swagger_css_url="https://cdn.staticfile.org/swagger-ui/5.9.0/swagger-ui.min.css",
            swagger_favicon_url="/static/image/favicon.ico",
        )
    app.add_route(docs_url, swagger_ui_html, include_in_schema=False)

    # ReDoc
    async def redoc_html(req: Request) -> HTMLResponse:
        return get_redoc_html(
            openapi_url=app_config['openapi_url'],
            title=str(app_config['title']) + " - ReDoc页面",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
            redoc_favicon_url="/static/image/favicon.ico",
            with_google_fonts=False,
        )
    app.add_route(redoc_url, redoc_html, include_in_schema=False)
