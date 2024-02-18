from util.flask.flask_models import UrlPatternItem
from web import index, user, audio, download

url_pattern_list: list[UrlPatternItem] = [
    UrlPatternItem(url_prefix=f'/', blueprint=index.app),
    UrlPatternItem(url_prefix=f'/{user.app_name}', blueprint=user.app),
    UrlPatternItem(url_prefix=f'/{download.app_name}', blueprint=download.app),
    UrlPatternItem(url_prefix=f'/{audio.app_name}', blueprint=audio.app),
]

