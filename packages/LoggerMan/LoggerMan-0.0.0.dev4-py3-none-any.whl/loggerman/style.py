from typing import NamedTuple as _NamedTuple, Literal as _Literal
from markitup import sgr as _sgr


class ConsoleHeadingStyle(_NamedTuple):
    sgr_sequence: str
    margin_top: int = 1
    margin_bottom: int = 0
    width: int = 0
    align: _Literal["left", "right", "center"] = "left"


class LogStyle(_NamedTuple):
    symbol: str
    title_sgr_sequence: str = _sgr.style(text_styles="bold")
    title_html_template: str = "<b>{}</b>"
    msg_sgr_sequence: str = ""
    msg_html_template: str = "{}"
    code_title: str = "Code"
    code_title_sgr_sequence: str = ""
    code_title_html_template: str = "{}"
    code_sgr_sequence: str = ""
    code_html_template: str = "<pre>{}</pre>"
    title_msg_seperator_text: str = ": "
    title_msg_seperator_html: str = ": "
    title_msg_seperator_github_annotation: str = ": "
    code_title_seperatpr_text: str = ": "
    traceback_title: str = "Traceback"
    traceback_title_sgr_sequence: str = ""
    traceback_title_html_template: str = "{}"
    traceback_sgr_sequence: str = ""
    traceback_html_template: str = "<pre>{}</pre>"
    traceback_title_seperator_text: str = ": "