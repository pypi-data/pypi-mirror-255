"""LoggerMan"""


from typing import Literal as _Literal, Type as _Type, Sequence as _Sequence, Any as _Any
from pathlib import Path as _Path

from markitup import sgr

from loggerman.logger import Logger, LogLevel
from loggerman.style import ConsoleHeadingStyle, LogStyle


def create(
    global_: bool = False,
    realtime: bool = True,
    github: bool = False,
    min_console_log_level: LogLevel | None = LogLevel.DEBUG,
    init_section_number: int = 1,
    exit_code_critical: int | None = 1,
    sectioner_exception_catch: _Type[Exception] | _Sequence[_Type[Exception]] | None = None,
    sectioner_exception_log_level: LogLevel | _Literal[
        "debug", "info", "notice", "warning", "error", "critical"
    ] = LogLevel.CRITICAL,
    sectioner_exception_return_value: _Any = None,
    output_html_filepath: str | _Path | None = "log.html",
    root_heading: str = "Log",
    html_title: str = "Log",
    html_style: str = "",
    h1_style: ConsoleHeadingStyle = ConsoleHeadingStyle(
        sgr_sequence=sgr.style(text_styles="bold", text_color=(150, 0, 170))
    ),
    h2_style: ConsoleHeadingStyle = ConsoleHeadingStyle(
        sgr_sequence=sgr.style(text_styles="bold", text_color=(25, 100, 175))
    ),
    h3_style: ConsoleHeadingStyle = ConsoleHeadingStyle(
        sgr_sequence=sgr.style(text_styles="bold", text_color=(100, 160, 0))
    ),
    h4_style: ConsoleHeadingStyle = ConsoleHeadingStyle(
        sgr_sequence=sgr.style(text_styles="bold", text_color=(200, 150, 0))
    ),
    h5_style: ConsoleHeadingStyle = ConsoleHeadingStyle(
        sgr_sequence=sgr.style(text_styles="bold", text_color=(240, 100, 0))
    ),
    h6_style: ConsoleHeadingStyle = ConsoleHeadingStyle(
        sgr_sequence=sgr.style(text_styles="bold", text_color=(220, 0, 35))
    ),
    debug_style: LogStyle = LogStyle(symbol="🔘"),
    info_style: LogStyle = LogStyle(symbol="ℹ️"),
    notice_style: LogStyle = LogStyle(symbol="❗"),
    warning_style: LogStyle = LogStyle(symbol="🚨"),
    error_style: LogStyle = LogStyle(symbol="🚫"),
    critical_style: LogStyle = LogStyle(symbol="⛔"),
    caller_symbol: str = "🔔",
) -> Logger:
    kwargs = locals()
    kwargs.pop("global_")
    if global_:
        global logger
    logger = Logger(**kwargs)
    return logger


logger: Logger = create(
    global_=True, realtime=False, output_html_filepath=None, sectioner_exception_catch=None
)
