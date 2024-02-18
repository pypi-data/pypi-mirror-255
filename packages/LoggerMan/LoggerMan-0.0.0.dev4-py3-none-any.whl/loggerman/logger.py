import sys
from enum import Enum as _Enum
from typing import (
    Literal as _Literal, Callable as _Callable, Type as _Type, Sequence as _Sequence, Any as _Any
)
import inspect as _inspect
import sys as _sys
import traceback as _traceback
from functools import wraps as _wraps
from textwrap import dedent as _dedent
from pathlib import Path as _Path
from markitup import html as _html, sgr as _sgr
import actionman as _actionman

from loggerman.protocol import Stringable as _Stringable
from loggerman.style import ConsoleHeadingStyle as _ConsoleHeadingStyle, LogStyle as _LogStyle


class LogLevel(_Enum):
    DEBUG = "debug"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Logger:

    _LOG_LEVEL_TO_INT = {
        LogLevel.DEBUG: 0,
        LogLevel.INFO: 1,
        LogLevel.NOTICE: 2,
        LogLevel.WARNING: 3,
        LogLevel.ERROR: 4,
        LogLevel.CRITICAL: 5,
        None: 6,
    }

    def __init__(
        self,
        realtime: bool,
        github: bool,
        min_console_log_level: LogLevel | None,
        init_section_number: int,
        exit_code_critical: int | None,
        sectioner_exception_catch: _Type[Exception] | _Sequence[_Type[Exception]] | None,
        sectioner_exception_log_level: LogLevel | _Literal[
            "debug", "info", "notice", "warning", "error", "critical"
        ],
        sectioner_exception_return_value: _Any,
        output_html_filepath: str | _Path | None,
        root_heading: str,
        html_title: str,
        html_style: str,
        h1_style: _ConsoleHeadingStyle,
        h2_style: _ConsoleHeadingStyle,
        h3_style: _ConsoleHeadingStyle,
        h4_style: _ConsoleHeadingStyle,
        h5_style: _ConsoleHeadingStyle,
        h6_style: _ConsoleHeadingStyle,
        debug_style: _LogStyle,
        info_style: _LogStyle,
        notice_style: _LogStyle,
        warning_style: _LogStyle,
        error_style: _LogStyle,
        critical_style: _LogStyle,
        caller_symbol: str,
    ):
        self._realtime = realtime
        self._github = github
        self._min_console_level = self._LOG_LEVEL_TO_INT[min_console_log_level]
        self._next_section_num = [init_section_number]
        error_msg_exit_code = (
            "Argument `exit_code_on_error` must be a positive integer or None, "
            f"but got '{exit_code_critical}' (type: {type(exit_code_critical)})."
        )
        if isinstance(exit_code_critical, int):
            if exit_code_critical <= 0:
                raise ValueError(error_msg_exit_code)
        elif exit_code_critical is not None:
            raise TypeError(error_msg_exit_code)
        self._default_exit_code = exit_code_critical
        self._sectioner_exception_catch: tuple[_Type[Exception], ...] = tuple(
            sectioner_exception_catch
        ) if isinstance(sectioner_exception_catch, _Sequence) else (
            tuple() if sectioner_exception_catch is None else (sectioner_exception_catch, )
        )
        self._sectioner_exception_log_level = sectioner_exception_log_level if isinstance(
            sectioner_exception_log_level, LogLevel
        ) else LogLevel(sectioner_exception_log_level)
        self._sectioner_exception_return = sectioner_exception_return_value
        self._output_html_filepath = _Path(output_html_filepath).resolve() if output_html_filepath else None
        self._h_style = {
            1: h1_style,
            2: h2_style,
            3: h3_style,
            4: h4_style,
            5: h5_style,
            6: h6_style,
        }
        self._level_style = {
            LogLevel.DEBUG: debug_style,
            LogLevel.INFO: info_style,
            LogLevel.NOTICE: notice_style,
            LogLevel.WARNING: warning_style,
            LogLevel.ERROR: error_style,
            LogLevel.CRITICAL: critical_style,
        }
        self._symbol_caller = caller_symbol

        if self._output_html_filepath:
            self._output_html_filepath.parent.mkdir(parents=True, exist_ok=True)
            self._output_html_filepath.touch(exist_ok=True)

        self._curr_section = ""

        self._open_grouped_sections = 0
        self._out_of_section: bool = False

        self._log_console: str = ""
        html_intro = _dedent(
            f"""
            <!DOCTYPE html>
            <html>
            <head>
            <title>{html_title}</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            """
        ).lstrip()
        if html_style:
            html_intro += f"<style>\n{html_style}\n</style>\n"
        self._log_html: str = f"{html_intro}</head>\n<body>\n"
        self._html_file_end = "</body>\n</html>\n"
        self._html_num_chars_at_end = -len(self._html_file_end)
        if self._realtime and self._output_html_filepath:
            with open(self._output_html_filepath, 'w') as f:
                f.write(f"{self._log_html}{self._html_file_end}")
        self.section(title=root_heading, stack_up=1)
        return

    def sectioner(
        self,
        title: str = "",
        group: bool = True,
        stack_up: int = 0,
        catch_exception_set: _Type[Exception] | _Sequence[_Type[Exception]] | None = None,
        catch_exception_add: _Type[Exception] | _Sequence[_Type[Exception]] | None = None,
        catch_exception_remove: _Type[Exception] | _Sequence[_Type[Exception]] | None = None,
        exception_log_level: LogLevel | _Literal[
            "debug", "info", "notice", "warning", "error", "critical"
        ] | None = None,
        exception_handler: _Callable | None = None,
        exception_return_value: _Any = None,
        sys_exit: bool | None = None,
        exit_code: int | None = None,
    ):
        """Decorator for sectioning a function or method."""
        def func_caller_no_catch(func: _Callable, *args, **kwargs):
            return func(*args, **kwargs)

        def fun_caller_with_catch(func: _Callable, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions_to_catch:
                handler_return = exception_handler() if exception_handler else None
                self.log(
                    level=log_level_for_exception,
                    sys_exit=sys_exit,
                    exit_code=exit_code,
                )
                return return_value_from_exception or handler_return

        if catch_exception_set is not None:
            exceptions_to_catch = tuple(catch_exception_set) if isinstance(
                catch_exception_set, _Sequence
            ) else (catch_exception_set, )
        else:
            exceptions_to_catch = list(self._sectioner_exception_catch)
            if isinstance(catch_exception_add, _Sequence):
                exceptions_to_catch.extend(catch_exception_add)
            elif catch_exception_add is not None:
                exceptions_to_catch.append(catch_exception_add)
            if isinstance(catch_exception_remove, _Sequence):
                for exception in catch_exception_remove:
                    try:
                        exceptions_to_catch.remove(exception)
                    except ValueError:
                        pass
            elif catch_exception_remove is not None:
                try:
                    exceptions_to_catch.remove(catch_exception_remove)
                except ValueError:
                    pass
            exceptions_to_catch = tuple(exceptions_to_catch)

        if not exceptions_to_catch:
            function_caller_func = func_caller_no_catch
        else:
            log_level_for_exception = exception_log_level or self._sectioner_exception_log_level
            return_value_from_exception = (
                exception_return_value if exception_return_value is not None
                else self._sectioner_exception_return
            )
            function_caller_func = fun_caller_with_catch

        def section_decorator(func: _Callable):
            @_wraps(func)
            def section_wrapper(*args, **kwargs):
                if title:
                    self.section(title=title, group=group, stack_up=stack_up)
                result = function_caller_func(func, *args, **kwargs)
                if title:
                    self.section_end()
                return result
            return section_wrapper
        return section_decorator

    def section(self, title: str, group: bool = False, stack_up: int = 0):
        section_level = min(len(self._next_section_num), 6)
        section_num = ".".join([str(num) for num in self._next_section_num])
        self._curr_section = f"{section_num}  {title}"
        fully_qualified_name = self._caller_name(stack_up=stack_up)
        caller_entry_html = f"{self._symbol_caller} Caller: <code>{fully_qualified_name}</code>"
        heading_html = _html.h(section_level, self._curr_section)
        output_html = f"{heading_html}\n{caller_entry_html}"
        heading_console = self._format_heading_console(
            self._curr_section, **self._h_style[section_level]._asdict()
        )
        output_console = f"{heading_console}  [{fully_qualified_name}]"
        if self._github:
            if group and not self._open_grouped_sections:
                output_console = _actionman.log.group_open(title=output_console, print_=False)
            if group or self._open_grouped_sections:
                self._open_grouped_sections += 1
        self._submit(console=output_console, file=output_html)
        self._next_section_num.append(1)
        return

    def section_end(self):
        if self._open_grouped_sections:
            self._open_grouped_sections -= 1
            if not self._open_grouped_sections:
                self._submit_console(text=_actionman.log.group_close(print_=False))
        if len(self._next_section_num) > 2:
            self._next_section_num.pop()
        else:
            # TODO: Give some warning or raise some error here
            pass
        self._next_section_num[-1] += 1
        self._out_of_section = True
        return

    def log(
        self,
        level: LogLevel | _Literal["debug", "info", "notice", "warning", "error", "critical"],
        title: _Stringable = "",
        msg: _Stringable = "",
        code: _Stringable = "",
        code_title: _Stringable | None = None,
        sys_exit: bool | None = None,
        exit_code: int | None = None,
        stack_up: int = 0,
    ):
        level = level if isinstance(level, LogLevel) else LogLevel(level)
        output_console, output_html, github_annotation_msg = self._format_entry(
            level=level,
            title=title,
            message=msg,
            code=code,
            code_title=code_title,
        )
        if level is LogLevel.DEBUG and self._github:
            output_console = _actionman.log.debug(
                message=output_console,
                print_=False,
            )
        self._submit(console=output_console, file=output_html, level=level)
        if level is LogLevel.CRITICAL:
            if sys_exit is None:
                sys_exit = self._default_exit_code is not None
            if sys_exit and self._open_grouped_sections:
                self._submit_console(text=_actionman.log.group_close(print_=False))
        fatal = level is LogLevel.CRITICAL and sys_exit
        if self._github and level in (
            LogLevel.NOTICE, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL
        ):
            caller_name = self._caller_name(stack_up=stack_up)
            output_annotation = _actionman.log.annotation(
                typ=level.value if level is not LogLevel.CRITICAL else "error",
                message=github_annotation_msg,
                title=f"{'FATAL ERROR: ' if fatal else ''}{self._curr_section} [caller: `{caller_name}`]",
                print_=False
            )
            self._submit_console(text=output_annotation)
        if level is LogLevel.CRITICAL and sys_exit:
            exit_code = exit_code or self._default_exit_code
            _sys.exit(exit_code)
        return

    def debug(
        self,
        title: _Stringable = "",
        msg: _Stringable = "",
        code: _Stringable = "",
        code_title: _Stringable | None = None,
    ) -> None:
        self.log(level=LogLevel.WARNING, title=title, msg=msg, code=code, code_title=code_title)
        return

    def info(
        self,
        title: _Stringable = "",
        msg: _Stringable = "",
        code: _Stringable = "",
        code_title: _Stringable | None = None
    ) -> None:
        self.log(level=LogLevel.WARNING, title=title, msg=msg, code=code, code_title=code_title)
        return

    def notice(
        self,
        title: _Stringable = "",
        msg: _Stringable = "",
        code: _Stringable = "",
        code_title: _Stringable | None = None,
        stack_up: int = 0,
    ) -> None:
        self.log(
            level=LogLevel.WARNING, title=title, msg=msg, code=code, code_title=code_title, stack_up=stack_up
        )
        return

    def warning(
        self,
        title: _Stringable = "",
        msg: _Stringable = "",
        code: _Stringable = "",
        code_title: _Stringable | None = None,
        stack_up: int = 0,
    ) -> None:
        self.log(
            level=LogLevel.WARNING, title=title, msg=msg, code=code, code_title=code_title, stack_up=stack_up
        )
        return

    def error(
        self,
        title: _Stringable = "",
        msg: _Stringable = "",
        code: _Stringable = "",
        code_title: _Stringable | None = None,
        stack_up: int = 0,
    ) -> None:
        self.log(
            level=LogLevel.WARNING, title=title, msg=msg, code=code, code_title=code_title, stack_up=stack_up
        )
        return

    def critical(
        self,
        title: _Stringable = "",
        msg: _Stringable = "",
        code: _Stringable = "",
        code_title: _Stringable | None = None,
        sys_exit: bool | None = None,
        exit_code: int | None = None,
        stack_up: int = 0,
    ):
        self.log(
            level=LogLevel.WARNING,
            title=title,
            msg=msg,
            code=code,
            code_title=code_title,
            sys_exit=sys_exit,
            exit_code=exit_code,
            stack_up=stack_up,
        )
        return

    @property
    def console_log(self):
        return self._log_console

    @property
    def html_log(self):
        return f"{self._log_html}{self._html_file_end}"

    def _format_entry(
        self,
        level: LogLevel,
        title: _Stringable,
        message: _Stringable,
        code: _Stringable,
        code_title: _Stringable | None,
    ):
        style = self._level_style[level]
        curr_exception = sys.exception()
        title_str = str(title) or (curr_exception.__class__.__name__ if curr_exception else "")
        msg_str = str(message) or (str(curr_exception) if curr_exception else "")
        code_str = str(code)
        code_title_str = str(code_title) if code_title else style.code_title
        traceback = _traceback.format_exc() if curr_exception else ""

        output_console = f"{style.symbol} "
        output_html = ""
        output_annotation_msg = ""

        if title:
            output_console += _sgr.format(text=title_str, control_sequence=style.title_sgr_sequence)
            output_html = f"{style.symbol} {style.title_html_template.format(title_str)}"
            output_annotation_msg = title_str
        if message:
            if title:
                output_console += style.title_msg_seperator_text
                output_html += style.title_msg_seperator_html
                output_annotation_msg += style.title_msg_seperator_github_annotation
            else:
                output_html += f"{style.symbol} "
            output_console += _sgr.format(text=msg_str, control_sequence=style.msg_sgr_sequence)
            output_html += style.msg_html_template.format(msg_str)
            output_annotation_msg += msg_str
        if code:
            if title or message:
                output_console += "\n"
                html_summary_intro = ""
            else:
                output_annotation_msg += f"{code_title_str}: {code_str}"
                html_summary_intro = f"{style.symbol} "
            code_title_formatted = _sgr.format(
                text=code_title_str, control_sequence=style.code_title_sgr_sequence
            )
            code_formatted = _sgr.format(text=code_str, control_sequence=style.code_sgr_sequence)
            output_console += f"{code_title_formatted}{style.code_title_seperatpr_text}{code_formatted}"
            output_html += str(
                _html.details(
                    summary=f"{html_summary_intro}{style.code_title_html_template.format(code_title_str)}",
                    content=style.code_html_template.format(code_str),
                )
            )
        if traceback:
            if title or message or code:
                output_console += "\n"
                html_summary_intro = ""
            else:
                html_summary_intro = f"{style.symbol} "
            traceback_title_formatted = _sgr.format(
                text=style.traceback_title, control_sequence=style.traceback_title_sgr_sequence
            )
            traceback_formatted = _sgr.format(text=traceback, control_sequence=style.traceback_sgr_sequence)
            output_console += (
                f"{traceback_title_formatted}{style.traceback_title_seperator_text}{traceback_formatted}"
            )
            traceback_title_html = style.traceback_title_html_template.format(style.traceback_title)
            output_html += str(
                _html.details(
                    summary=f"{html_summary_intro}{traceback_title_html}",
                    content=style.traceback_html_template.format(traceback),
                )
            )
        return output_console, str(_html.ul([output_html])), output_annotation_msg

    def _submit(
        self,
        console: str,
        file: str | _html.Element | _html.ElementCollection,
        level: LogLevel | None = None
    ):
        self._submit_console(text=console, level=level)
        self._submit_html(html=file)
        return

    def _submit_console(self, text: str, level: LogLevel | None = None):
        self._log_console += f"{text}\n"
        if self._realtime and (self._github or level is None or self._LOG_LEVEL_TO_INT[level] >= self._min_console_level):
            _sys.stdout.flush()  # Flush stdout buffer before printing the exception
            _sys.stderr.flush()  # Flush stderr buffer before printing the exception
            print(text, flush=True)
        return

    def _submit_html(self, html: str | _html.Element | _html.ElementCollection):
        file_entry = f"{html}\n"
        self._log_html += file_entry
        if self._realtime and self._output_html_filepath:
            with open(self._output_html_filepath, 'rb+') as file:
                file.seek(self._html_num_chars_at_end, 2)
                file.write(f"{file_entry}{self._html_file_end}".encode('utf-8'))
        return

    @staticmethod
    def _caller_name(stack_up: int = 0) -> str:
        stack = _inspect.stack()
        # The caller is the second element in the stack list
        caller_frame = stack[2 + stack_up]
        module = _inspect.getmodule(caller_frame[0])
        module_name = module.__name__ if module else "<module>"
        # Get the function or method name
        func_name = caller_frame.function
        # Combine them to get a fully qualified name
        fully_qualified_name = f"{module_name}.{func_name}"
        return fully_qualified_name

    @staticmethod
    def _format_heading_console(
        title: str,
        width: int,
        align: _Literal["left", "right", "center"],
        margin_top: int,
        margin_bottom: int,
        sgr_sequence: str,
    ) -> str:
        if align == "left":
            aligned_title = title.ljust(width)
        elif align == "right":
            aligned_title = title.rjust(width)
        else:
            aligned_title = title.center(width)
        heading_box = _sgr.format(text=aligned_title, control_sequence=sgr_sequence)
        margin_top = "\n" * margin_top
        margin_bottom = "\n" * margin_bottom
        return f"{margin_top}{heading_box}{margin_bottom}"
