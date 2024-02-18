# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""Bliss REPL (Read Eval Print Loop)"""

from prompt_toolkit.styles.pygments import style_from_pygments_cls
from prompt_toolkit.output.plain_text import PlainTextOutput
from prompt_toolkit import print_formatted_text, HTML, ANSI
from pygments.styles import get_style_by_name
from pygments.util import ClassNotFound

import asyncio
import builtins
import html
import re
import os
import sys
import socket
import functools
import gevent
import signal
import logging
import platform
from collections import deque
from contextlib import contextmanager
from datetime import datetime
from typing import Optional

import ptpython.layout
from prompt_toolkit.output.color_depth import ColorDepth

# imports needed to have control over _execute of ptpython
from prompt_toolkit.keys import Keys
from prompt_toolkit.utils import is_windows
from prompt_toolkit.filters import has_focus
from prompt_toolkit.enums import DEFAULT_BUFFER

from bliss.shell import log_utils
from bliss.shell.cli.prompt import BlissPrompt
from bliss.shell.cli.typing_helper import TypingHelper
from bliss.shell.cli.ptpython_statusbar_patch import NEWstatus_bar, TMUXstatus_bar
from bliss.shell.cli.no_thread_repl import NoThreadPythonRepl
from bliss.shell.cli.formatted_traceback import BlissTraceback, pprint_traceback
from bliss.shell import standard

from bliss import set_bliss_shell_mode, current_session, global_log
from bliss.common.proxy import Proxy
from bliss.common import logtools
from bliss.common.protected_dict import ProtectedDict
from bliss.common.utils import Singleton
from bliss.common import constants
from bliss.common.session import DefaultSession
from bliss import release
from bliss.config import static
from bliss.config.conductor.client import get_default_connection
from bliss.shell.standard import info
from bliss.shell.data.display import StepScanProgress
from bliss.common.logtools import elogbook
from bliss.common.protocols import ErrorReportInterface, HasInfo
from bliss.scanning import scan as scan_module
from bliss.physics.units import ur
from bliss.config.settings import OrderedHashObjSetting
from bliss.shell.formatters.string import removed_ansi_sequence

logger = logging.getLogger(__name__)
builtin_print = builtins.print


# =================== ERROR REPORTING ============================


class ErrorReport(ErrorReportInterface):
    """
    Manage the behavior of the error reporting in the shell.

    - ErrorReport.expert_mode = False (default) => prints a user friendly error message without traceback
    - ErrorReport.expert_mode = True            => prints the full error message with traceback

    - ErrorReport.last_error stores the last error traceback

    """

    def __init__(self, style, output):
        self._expert_mode = False
        self._history = deque(maxlen=100)
        self._nb_discarded = 0
        self._current_style = style
        self._output = output
        self._is_loading_config = False

    @property
    def output(self):
        return self._output

    @property
    def expert_mode(self):
        return self._expert_mode

    @expert_mode.setter
    def expert_mode(self, enable):
        self._expert_mode = bool(enable)

    def append(self, error):
        if len(self._history) == self._history.maxlen:
            self._nb_discarded += 1
        self._history.append(error)

    def __len__(self):
        return len(self._history) + self._nb_discarded

    def __getitem__(self, index):
        if index < 0:
            index = len(self) + index

        if index < 0 or index >= len(self):
            raise IndexError("Index out of range")
        deque_index = index - self._nb_discarded
        if deque_index < 0 or deque_index >= len(self._history):
            raise IndexError(
                f"Exception[{index}] has been discarded, only the last {self._history.maxlen} exceptions are kept in history."
            )

        return self._history[deque_index]

    @property
    def is_loading_config(self):
        return self._is_loading_config

    @is_loading_config.setter
    def is_loading_config(self, loading):
        self._is_loading_config = bool(loading)

    def display_exception(self, exc_type, exc_value, tb, _with_elogbook=True):
        exc_logger = logging.getLogger("exceptions")
        print = functools.partial(builtin_print, file=self._output)

        # BlissTraceback captures traceback information without holding any reference on its content
        fmt_tb = BlissTraceback(exc_type, exc_value, tb)

        # store BlissTraceback for later formatting
        self._history.append(fmt_tb)

        # publish full error to logger
        exc_logger.error(
            fmt_tb.format(
                disable_blacklist=False,
                max_nb_locals=15,
                max_local_len=200,
                show_locals=True,
            )
        )

        # Adapt the error message depending on the expert_mode
        if self.expert_mode:
            fmt_tb = self[-1].format(
                disable_blacklist=False,
                max_nb_locals=15,
                max_local_len=200,
                show_locals=True,
            )
            pprint_traceback(fmt_tb, self._current_style)
        else:
            if self.is_loading_config or isinstance(
                exc_value, static.ObjectCreationFailed
            ):
                e = exc_value
                causes = [e]
                while isinstance(e, static.ObjectCreationFailed):
                    e = e.__cause__
                    causes.append(e)

                if self.is_loading_config:
                    error_count_msg = f"[{len(self)-1}] "
                else:
                    error_count_msg = ""

                fmt_error = ""
                for i, e in enumerate(causes):
                    if i == 0:
                        fmt_error += error_count_msg
                    else:
                        fmt_error += (
                            f"{' ' * len(error_count_msg)}  {'    ' * (i - 1)}└─"
                        )
                    if isinstance(e, static.ObjectCreationFailed):
                        name = html.escape(e.name)
                        filename = html.escape(e.filename)
                        if i == 0:
                            fmt_error += f"Initialization of '<bold>{name}</bold>' <red>FAILED</red>  (see '<bold>{filename}</bold>')\n"
                        else:
                            fmt_error += f"Depending on initialization of '<bold>{name}</bold>'  (see '<bold>{filename}</bold>')\n"
                    else:
                        class_name = html.escape(e.__class__.__name__)
                        error = html.escape(str(e))
                        fmt_error += f"<red>{class_name}</red>: {error}\n"
                print_formatted_text(HTML(fmt_error), end="", output=self._output)

                if not self.is_loading_config:
                    print(f"( for more details type cmd 'last_error({len(self)-1})' )")
            else:
                print(
                    f"!!! === {exc_type.__name__}: {exc_value} === !!! ( for more details type cmd 'last_error({len(self)-1})' )"
                )

        if _with_elogbook:
            try:
                elogbook.error(f"{exc_type.__name__}: {exc_value}")
            except Exception:
                self.display_exception(exc_type, exc_value, tb, _with_elogbook=False)


__all__ = ("BlissRepl", "embed", "cli", "configure_repl")

#############

# patch ptpython completer, and jedi
import bliss.shell.cli.ptpython_completer_patch  # noqa: F401,E402

#############


class BlissOutput:
    """This class is used to keep track of the output history.

    It is meant to be used as a mixin with a prompt toolkit output
    """

    _MAXLEN = 20

    def __init__(self, file_output_dict=None):
        self.__file_output_dict = {} if file_output_dict is None else file_output_dict
        self._capture = False
        self._output_buffer = []
        self._log_stdout_buffer = []
        self._cell_counter = 0
        self._cell_output_history = deque(maxlen=self._MAXLEN)

    @property
    @contextmanager
    def capture_stdout(self):
        self._capture = True
        try:
            yield
        finally:
            self._capture = False

    def finalize_cell(self):
        """Store the current buffered output as 1 cell output in the history."""
        if self._output_buffer:
            output = "".join(
                [x if isinstance(x, str) else str(x) for x in self._output_buffer]
            )
            output = re.sub(
                r"^(\s+Out\s\[\d+\]:\s+)", "", output, count=1, flags=re.MULTILINE
            )
            self._output_buffer.clear()
        else:
            output = None
        self._cell_output_history.append(output)
        self._cell_counter += 1

    def __getitem__(self, item: int) -> Optional[str]:
        """Note that the ptpython cell index starts counting from 1

        item > 0 will be interpreted as the cell index
        item < 0 will be interpreted as the most recent cell output (-1 is the last output)
        item == 0 raise IndexError

        The output value of a cell without output is `None`.
        """
        if not isinstance(item, int):
            raise TypeError(item)
        if self._cell_counter == 0:
            raise IndexError("No output.")
        if item > 0:
            # convert cell index to queue index
            idx = item - self._cell_counter - 1
            if idx >= 0:
                raise IndexError(f"the last cell is OUT [{self._cell_counter}]")
        elif item == 0:
            idx_min = max(self._cell_counter - self._MAXLEN + 1, 1)
            raise IndexError(f"the first available cell is OUT [{idx_min}]")
        elif (item + self._cell_counter) < 0:
            idx_min = max(self._cell_counter - self._MAXLEN + 1, 1)
            raise IndexError(f"the first available cell is OUT [{idx_min}]")
        else:
            idx = item
        try:
            return self._cell_output_history[idx]
        except IndexError:
            idx_min = max(self._cell_counter - self._MAXLEN + 1, 1)
            raise IndexError(f"the first available cell is OUT [{idx_min}]") from None

    def write(self, data):
        if self._capture:
            self._output_buffer.append(data)
        if "\x1b" in data or "\r" in data:
            super().write_raw(data)
        else:
            super().write(data)
            # buffering data for log_stdout file
            if self.__file_output_dict:
                self._log_stdout_buffer.append(data)
        if data.endswith("\n"):
            try:
                self.flush()
            except IOError:
                pass

    def flush(self):
        # flush data to stdout file
        if self.__file_output_dict:
            data = "".join(self._log_stdout_buffer)
            self._log_stdout_buffer.clear()
            for _, file in self.__file_output_dict.items():
                if file:
                    try:
                        builtin_print(
                            data.replace("\r\n", "\n"), file=file, end="", flush=True
                        )
                    except Exception as e:
                        self.__file_output_dict.clear()
                        print(f"Cannot flush stdout data to file: {e}")

        # flush app.output data
        return super().flush()

    def isatty(self):
        return True

    def elog_add(self, index=-1, beamline_only: Optional[bool] = None):
        try:
            comment = self[index]
        except IndexError as e:
            logtools.log_warning(self, str(e))
        except TypeError:
            logtools.log_warning(
                self,
                "elog_add should be called with a number, for example 'elog_add(42)'",
            )
        else:
            if comment is not None:
                comment = removed_ansi_sequence(comment)
                elogbook.comment(comment, beamline_only=beamline_only)


class DummyPromptToolkitOutputWrapper(BlissOutput, PlainTextOutput):
    def __init__(self, output, file_output_dict=None):
        PlainTextOutput.__init__(self, output)
        BlissOutput.__init__(self, file_output_dict)


if sys.platform != "win32":
    from prompt_toolkit.output.vt100 import Vt100_Output
    from prompt_toolkit.utils import (
        get_bell_environment_variable,
        get_term_environment_variable,
    )
    from prompt_toolkit.data_structures import Size

    class Vt100PromptToolkitOutputWrapper(BlissOutput, Vt100_Output):
        def __init__(
            self, output, color_depth, rows=None, columns=None, file_output_dict=None
        ):
            term_from_env = get_term_environment_variable()
            bell_from_env = get_bell_environment_variable()

            def get_size():
                return Size(rows=rows or 24, columns=columns or 80)

            Vt100_Output.__init__(
                self,
                output.stdout,
                get_size,
                term=term_from_env,
                default_color_depth=color_depth,
                enable_bell=bell_from_env,
            )
            BlissOutput.__init__(self, file_output_dict)


@functools.singledispatch
def format_repl(arg):
    """Customization point format_repl for any types that need specific
    handling. This default implementation returns the __info__ if available.

    Usage:

    from bliss.shell.cli.repl import format_repl

    @format_repl.register
    def _(arg: Foo):
        # Returns the representation of Foo
        return f"{arg.bar}"
    """
    return arg


@format_repl.register
def _(arg: HasInfo):
    """Specialization for types that implement the __info__ protocol."""

    class _InfoResult:
        def __repr__(self):
            return info(arg)

    return _InfoResult()


@format_repl.register
def _(arg: ur.Quantity):
    """Specialization for Quantity"""

    class _QuantityResult:
        def __repr__(self):
            return f"{arg:~P}"  # short pretty formatting

    return _QuantityResult()


class BlissReplBase(NoThreadPythonRepl):
    def __init__(self, *args, **kwargs):
        prompt_label = kwargs.pop("prompt_label", "BLISS")
        title = kwargs.pop("title", None)
        style = kwargs.pop("style")
        log_stdout_setting_cache = kwargs.pop("log_stdout_setting_cache", None)

        # Catch and remove additional kwargs
        self.session_name = kwargs.pop("session_name", constants.DEFAULT_SESSION_NAME)
        if self.session_name is None:
            self.session_name = constants.DEFAULT_SESSION_NAME
        self.use_tmux = kwargs.pop("use_tmux", False)
        expert_error_report = kwargs.pop("expert_error_report", False)

        # patch ptpython statusbar
        if self.use_tmux and not is_windows():
            ptpython.layout.status_bar = TMUXstatus_bar
        else:
            ptpython.layout.status_bar = NEWstatus_bar

        super().__init__(*args, **kwargs)
        self.bliss_session = None
        self.bliss_prompt = BlissPrompt(self, prompt_label)
        self.all_prompt_styles["bliss"] = self.bliss_prompt
        self.prompt_style = "bliss"
        self.show_signature = True
        self.color_depth = ColorDepth.from_env()
        if self.color_depth is None:
            self.color_depth = ColorDepth.default()
        if title:
            self.terminal_title = title

        self._file_output_dict = {}
        if sys.platform == "win32" or isinstance(self.app.output, PlainTextOutput):
            self.app.output = DummyPromptToolkitOutputWrapper(
                self.app.output, self._file_output_dict
            )
        else:
            self.app.output = Vt100PromptToolkitOutputWrapper(
                self.app.output,
                self.color_depth,
                file_output_dict=self._file_output_dict,
            )

        def session_stream():
            """Depending on the current session, return the right stream for output"""
            try:
                pt_output = current_session._pt_output
            except AttributeError:
                pt_output = self.app.output
            if pt_output is None:
                # in tests, maybe current_session._pt_output is not initialized
                # (if initialize_session has not been called)
                pt_output = self.app.output
            return pt_output

        global_log.set_stdout_handler_stream(Proxy(session_stream))

        @functools.wraps(print)
        def session_print(*args, **kwargs):
            """Depending on the current session, print on the right output"""
            kwargs.setdefault("file", session_stream())
            kwargs.setdefault("flush", True)
            return builtin_print(*args, **kwargs)

        builtins.print = session_print

        def session_print_formatted_text_html(text, **kwargs):
            kwargs.setdefault("output", session_stream())
            return print_formatted_text(HTML(text), **kwargs)

        def session_print_formatted_text_ansi(text, **kwargs):
            kwargs.setdefault("output", session_stream())
            return print_formatted_text(ANSI(text), **kwargs)

        self.get_globals()["__print_html"] = session_print_formatted_text_html
        self.get_globals()["__print_ansi"] = session_print_formatted_text_ansi
        self.get_globals()["__elog_add"] = self.app.output.elog_add

        # stdout files duplication (load settings)
        if log_stdout_setting_cache == "redis":
            self._stdout_settings = OrderedHashObjSetting(
                f"{self.session_name}_stdout_settings"
            )
        else:
            self._stdout_settings = (
                {}
            )  # in case BEACON/REDIS is not running, like in tests

        try:
            theme = style_from_pygments_cls(get_style_by_name(style))
        except ClassNotFound:
            print(
                f"Unknown color style class: {style}. using default. (check your bliss.ini)."
            )
            theme = style_from_pygments_cls(get_style_by_name("default"))

        self.install_ui_colorscheme("bliss_ui", theme)
        self.use_ui_colorscheme("bliss_ui")
        self.install_code_colorscheme("bliss_code_ui", theme)
        self.use_code_colorscheme("bliss_code_ui")

        # PTPYTHON SHELL PREFERENCES
        self.enable_history_search = True
        self.show_status_bar = True
        self.confirm_exit = True
        self.enable_mouse_support = False

        if self.use_tmux:
            self.exit_message = (
                "Do you really want to close session? (CTRL-B D to detach)"
            )

        self.typing_helper = TypingHelper(self)

        self.error_report = ErrorReport(self._current_style, self.app.output)
        self.error_report.expert_mode = expert_error_report

    def initialize_session(self, early_log_info=None):
        print = functools.partial(builtin_print, file=self.app.output)

        _version = "version %s" % release.version
        _hostname = platform.node()

        # Beacon host/port
        try:
            _host = get_default_connection()._host
            _port = str(get_default_connection()._port)
        except Exception:
            _host = "UNKNOWN"
            _port = "UNKNOWN"

        # Conda environment
        try:
            _env_name = os.environ["CONDA_DEFAULT_ENV"]
            _conda_env = "(in %s Conda environment)" % _env_name
        except KeyError:
            _conda_env = ""

        print("")
        print(f"Welcome to BLISS {_version} running on {_hostname} {_conda_env}")
        print("Copyright (c) Beamline Control Unit, ESRF")
        print("-")
        print(f"Connected to Beacon server on {_host} (port {_port})")

        if early_log_info is not None and early_log_info.count > 0:
            print()
            print(
                f"During the import {early_log_info.count} warnings were ignored. Restart BLISS with --debug to display them."
            )

        config = static.get_config()
        if config.invalid_yaml_files:
            print()
            print(
                f"Ignored {len(config.invalid_yaml_files)} YAML file(s) due to parsing error(s), use config.parsing_report() for details.\n"
            )

        self.app.output.flush()

        # Setup(s)
        if self.session_name == constants.DEFAULT_SESSION_NAME:
            self.bliss_session = DefaultSession()
        else:
            # we will lock the session name
            # this will prevent to start serveral bliss shell
            # with the same session name
            # lock will only be released at the end of process
            default_cnx = get_default_connection()
            try:
                default_cnx.lock(self.session_name, timeout=1.0)
            except RuntimeError:
                try:
                    lock_dict = default_cnx.who_locked(self.session_name)
                except RuntimeError:  # Beacon is to old to answer
                    raise RuntimeError(f"{self.session_name} is already started")
                else:
                    raise RuntimeError(
                        f"{self.session_name} is already running on %s"
                        % lock_dict.get(self.session_name)
                    )

            # set the client name to something useful
            try:
                default_cnx.set_client_name(
                    f"host:{socket.gethostname()},pid:{os.getpid()} cmd: **bliss -s {self.session_name}**"
                )
            except RuntimeError:  # Beacon is too old
                pass

            print("%s: Loading config..." % self.session_name)
            self.bliss_session = config.get(self.session_name)

        self.bliss_session._set_pt_output(self.app.output)
        self.bliss_session.set_error_report(self.error_report)

        if self.bliss_session.setup(self.get_globals(), verbose=True):
            print("Done.")
        else:
            print("Warning: error(s) happened during setup, setup may not be complete.")
        print("")

        log = logging.getLogger("startup")
        log.info(
            f"Started BLISS version "
            f"{_version} running on "
            f"{_hostname} "
            f"{_conda_env} "
            f"connected to Beacon server {_host}"
        )

    def raw_eval(self, text):
        """Delegate eval to base class

        Note: called from tests
        """
        prompt = "".join(x for _, x in self.bliss_prompt.in_prompt())

        # force reevaluation of stdout file path in case it is using
        # the default fname wich depends on proposal and today day
        if not self._stdout_settings.get("fname"):
            self.enable_stdout_file()

        # log cmd in stdout file
        for path, file in self._file_output_dict.items():
            if file:
                print(f"\n{prompt}{text}", file=file, flush=True)

        return super().eval(text)

    ##
    # NB: next methods are overloaded
    ##
    def eval(self, text):
        result = None
        try:
            logging.getLogger("user_input").info(text)
            elogbook.command(text)
            with self.app.output.capture_stdout:
                result = self.raw_eval(text)
        except SystemExit:
            result = SystemExit  # this is a trick to let the finally code just pass
            raise
        except BaseException:
            # exception message is not captured, this is on purpose
            # (see test_elogbook_cmd_log_and_elog_add)
            self.error_report.display_exception(*sys.exc_info())
        finally:
            if result is None:
                # show_result will not be called, so we call it here
                self.app.output.finalize_cell()
        return result

    def show_result(self, result):
        """This is called when the return value of the command is not None."""
        try:
            result = format_repl(result)
        except BaseException:
            # display exception, but do not propagate and make shell to die
            self.error_report.display_exception(*sys.exc_info())
        else:
            with self.app.output.capture_stdout:
                ret = super().show_result(result)
            self.app.output.finalize_cell()
            return ret

    def _build_stdout_file_path(self, fdir, fname=None):
        if not fname:  # build a default file name
            now = datetime.now()
            fname = ""
            if hasattr(current_session.scan_saving, "beamline"):
                fname += f"{current_session.scan_saving.beamline}_"
            fname += f"{self.session_name}_{now.year}{now.month:02}{now.day:02}"
            if hasattr(current_session.scan_saving, "proposal_name"):
                fname += f"_{current_session.scan_saving.proposal_name}"
            fname += ".log"
        return os.path.join(fdir, fname)

    def enable_stdout_file(self, fdir=None, fname=None):
        """Enable stdout duplication to file"""
        if fdir is None:
            fdir = self._stdout_settings.get("fdir")

        if fname is None:
            fname = self._stdout_settings.get("fname")

        if fname and not fdir:
            raise RuntimeError(
                "Please specify a directory for the stdout log file first"
            )

        if fdir:
            abspath = self._build_stdout_file_path(fdir, fname)
            if abspath not in self._file_output_dict.keys():
                try:
                    file = open(abspath, "a")
                except Exception:
                    print(f"log_stdout: could not open file '{abspath}'")
                else:
                    self.disable_stdout_file()
                    self._stdout_settings["fdir"] = fdir
                    self._stdout_settings["fname"] = fname
                    self._file_output_dict[abspath] = file

    def disable_stdout_file(self):
        """Disable stdout duplication to file"""
        for stdoutfile in self._file_output_dict.values():
            stdoutfile.close()
        self._file_output_dict.clear()
        self._stdout_settings["fdir"] = None
        self._stdout_settings["fname"] = None

    def show_stdout_file(self):
        if not self._stdout_settings.get("fdir"):
            print("stdout logging is disabled")
        else:
            print(f"stdout is logged to {list(self._file_output_dict.keys())[0]}")

    def unpatch(self):
        """Release the stuffs patched on the system at the termination

        It have to be called externally.
        """
        builtins.print = builtin_print


class BlissRepl(BlissReplBase, metaclass=Singleton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._sigint_handler = gevent.signal_handler(
            signal.SIGINT, self.kill_current_eval
        )

        scan_module._scan_progress_class = lambda: StepScanProgress(
            output=self.app.output
        )


def configure_repl(repl):

    # intended to be used for testing as ctrl+t can be send via stdin.write(bytes.fromhex("14"))
    # @repl.add_key_binding(Keys.ControlT)
    # def _(event):
    #    sys.stderr.write("<<BLISS REPL TEST>>")
    #    text = repl.default_buffer.text
    #    sys.stderr.write("<<BUFFER TEST>>")
    #    sys.stderr.write(text)
    #    sys.stderr.write("<<BUFFER TEST>>")
    #    sys.stderr.write("<<HISTORY>>")
    #    sys.stderr.write(repl.default_buffer.history._loaded_strings[-1])
    #    sys.stderr.write("<<HISTORY>>")
    #    sys.stderr.write("<<BLISS REPL TEST>>")

    @repl.add_key_binding(
        Keys.ControlSpace, filter=has_focus(DEFAULT_BUFFER), eager=True
    )
    def _(event):
        """
        Initialize autocompletion at cursor.
        If the autocompletion menu is not showing, display it with the
        appropriate completions for the context.
        If the menu is showing, select the next completion.
        """

        b = event.app.current_buffer
        if b.complete_state:
            b.complete_next()
        else:
            b.start_completion(select_first=False)


def _archive_history(
    history_filename, file_size_thresh=10**6, keep_active_entries=1000
):
    if (
        os.path.exists(history_filename)
        and os.stat(history_filename).st_size > file_size_thresh
    ):
        with open(history_filename, "r") as f:
            lines = f.readlines()

        # history is handled as a list of entries (block of lines) to avoid splitting them while archiving
        entries = []
        entry = []
        for line in lines:
            if not line.isspace():
                entry.append(line)
            elif entry:
                entries.append(entry)
                entry = []
        if entry:
            entries.append(entry)

        now = datetime.now()
        archive_filename = f"{history_filename}_{now.year}{now.month:02}{now.day:02}"
        with open(archive_filename, "a") as f:
            for entry in entries[:-keep_active_entries]:
                f.write("".join(entry) + "\n")

        with open(history_filename, "w") as f:
            for entry in entries[-keep_active_entries:]:
                f.write("".join(entry) + "\n")


def cli(
    repl_class=BlissRepl,
    locals=None,
    session_name=None,
    vi_mode=False,
    startup_paths=None,
    use_tmux=False,
    expert_error_report=False,
    style="default",
    early_log_info=None,
    **kwargs,
):
    """
    Create a command line interface

    Args:
        session_name : session to initialize (default: None)
        vi_mode (bool): Use Vi instead of Emacs key bindings.
    """
    set_bliss_shell_mode(True)

    # Enable loggers
    elogbook.enable()  # destination: electronic logbook

    # user namespace
    user_ns = {"__builtins__": __builtins__}

    if session_name and not session_name.startswith(constants.DEFAULT_SESSION_NAME):
        session_id = session_name
        session_title = "Bliss shell ({0})".format(session_name)
        prompt_label = session_name.upper()
    else:
        session_id = "default"
        session_title = "Bliss shell"
        prompt_label = "BLISS"

    history_filename = ".bliss_%s_history" % (session_id)
    if is_windows():
        history_filename = os.path.join(os.environ["USERPROFILE"], history_filename)
    else:
        history_filename = os.path.join(os.environ["HOME"], history_filename)

    _archive_history(history_filename)

    protected_user_ns = ProtectedDict(user_ns)
    protected_user_ns["protect"] = protected_user_ns.protect
    protected_user_ns["unprotect"] = protected_user_ns.unprotect
    cmds = {k: standard.__dict__[k] for k in standard.__all__}
    protected_user_ns.update(cmds)
    protected_user_ns["history"] = lambda: print("Please press F3-key to view history!")
    protected_user_ns._protect(protected_user_ns)

    # Create REPL.
    repl = repl_class(
        get_globals=lambda: protected_user_ns,
        session_name=session_name,
        vi_mode=vi_mode,
        prompt_label=prompt_label,
        title=session_title,
        history_filename=history_filename,
        startup_paths=startup_paths,
        use_tmux=use_tmux,
        style=style,
        expert_error_report=expert_error_report,
        log_stdout_setting_cache="redis",
        **kwargs,
    )

    # Custom keybindings
    configure_repl(repl)

    def last_error(index=None, show_locals=False):
        error_report = user_ns["ERROR_REPORT"]

        if index is None:
            if len(error_report) == 0:
                print("None")
                return
            index = -1

        try:
            tb = error_report[index]
        except IndexError as e:
            print(e.args[0])
            return

        fmt_tb = tb.format(
            disable_blacklist=repl.error_report.expert_mode,
            max_nb_locals=15,
            max_local_len=200,
            show_locals=show_locals,
        )
        pprint_traceback(fmt_tb, repl._current_style, output=repl.error_report.output)

    # handle the last error report
    # (in the shell env only)
    protected_user_ns["last_error"] = last_error
    protected_user_ns._protect("last_error")

    try:
        repl.initialize_session(early_log_info)
    except Exception as e:
        if use_tmux:
            print("\n", "*" * 20, "\n", e, "\n", "*" * 20)
            gevent.sleep(10)  # just to let the eyes to see the message ;)
        raise

    # init repl stdout duplication to file
    repl.enable_stdout_file()

    return repl


def embed(*args, **kwargs):
    """
    Call this to embed bliss shell at the current point in your program
    """
    with log_utils.filter_warnings():
        cmd_line_i = cli(BlissRepl, *args, **kwargs)
        asyncio.run(cmd_line_i.run_async())
