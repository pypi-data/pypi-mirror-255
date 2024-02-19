from typing import Callable, Union, Optional

from pydantic import BaseModel, computed_field


class QuoteField(BaseModel):
    name: str
    fid_list: list
    source_data: Optional[dict] = None
    value_func: Callable

    @computed_field(title='值')
    def value(self):
        return self.value_func(self.source_data)

    @computed_field(title='源值')
    def source_value(self):
        return [self.source_data[tmp] for tmp in self.fid_list]


class QuoteItem:
    """行情项"""

    def __init__(self, fid_list: list = None):
        """
        初始化创建
        :param fid_list: 依赖字段列表
        """
        self._source = None
        self._source_fun: Callable[[Union[str, int]], Union[str, int]] = None
        self._txt = None
        self._txt_fun: Callable[[Union[str, int]], str] = None
        self._color = None
        self._color_fun: Callable[[Union[str, int]], str] = None
        self._html = None
        self._html_fun: Callable[[Union[str, int]], str] = None
        self._blink_html = None
        self._blink_html_fun: Callable[[Union[str, int]], str] = None
        self.fid_list = fid_list
        self.create_fun: Callable[[Union[str, int]], 'QuoteItem'] = None

    def run(self, data_input):
        """运行"""
        if self.create_fun:
            tmp_item = self.create_fun(data_input)
            tmp_item.fid_list = self.fid_list
            return tmp_item
        if self._source_fun:
            self._source = self._source_fun(data_input)
        if self._txt_fun:
            self._txt = self._txt_fun(data_input)
        if self._color_fun:
            self._color = self._color_fun(data_input)
        if self._html_fun:
            self._html = self._html_fun(data_input)
        if self._blink_html_fun:
            self._blink_html = self._blink_html_fun(data_input)
        return self

    @property
    def source(self):
        return self._source

    def set_source(self, source: Union[int, str, Callable]) -> 'QuoteItem':
        if isinstance(source, Callable):
            self._source_fun = source
        else:
            self._source = source
        return self

    @property
    def txt(self):
        return self._txt if self._txt else self._source

    def set_txt(self, txt: Union[int, str, Callable]) -> 'QuoteItem':
        if isinstance(txt, Callable):
            self._txt_fun = txt
        else:
            self._txt = txt
        return self

    @property
    def html(self):
        color_str = f' style="color:{self._color};"' if self._color else ''
        return self._html if self._html else f'<span{color_str}>{self._source}</span>'

    def set_html(self, html: Union[int, str, Callable]) -> 'QuoteItem':
        if isinstance(html, Callable):
            self._html_fun = html
        else:
            self._html = html
        return self

    @property
    def color(self):
        return self._color if self._color else None

    def set_color(self, color: Union[int, str, Callable]) -> 'QuoteItem':
        if isinstance(color, Callable):
            self._color_fun = color
        else:
            self._color = color
        return self

    @property
    def blink_html(self):
        return self._blink_html if self._blink_html else f'<span>{self._source}</span>'

    def set_blink_html(self, blink_html: Union[int, str, Callable]) -> 'QuoteItem':
        if isinstance(blink_html, Callable):
            self._blink_html_fun = blink_html
        else:
            self._blink_html = blink_html
        return self

    def set_create_fun(self, create_fun: Callable[[Union[str, int]], 'QuoteItem']) -> 'QuoteItem':
        self.create_fun = create_fun
        return self
