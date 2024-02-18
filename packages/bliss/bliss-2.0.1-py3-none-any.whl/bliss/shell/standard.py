# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Standard functions provided to the BLISS shell.
"""

from __future__ import annotations
from typing import Callable, Any

import contextlib
import inspect
import itertools
import logging
import os
import shutil
import socket
import subprocess
import sys
import time
import typing

import numpy  # noqa: F401
from pprint import pprint  # noqa: F401
from gevent import sleep, Timeout
from bliss.common.axis import Axis

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter

from prompt_toolkit import print_formatted_text, HTML, ANSI

import bliss
from bliss import global_map, global_log, current_session
from bliss.common import timedisplay
from bliss.common.plot import plot  # noqa
from bliss.common.standard import (  # noqa
    iter_counters,
    iter_axes_state,
    iter_axes_state_all,
    iter_axes_position,
    iter_axes_position_all,
    sync,
    info,
    _move,
    reset_equipment,
)
from bliss.common.standard import wid as std_wid
from bliss.common.event import connect
from bliss.controllers.mca.base import BaseMCA
from bliss.controllers.lima.limatools import *  # noqa: F403
from bliss.controllers.lima import limatools
from bliss.controllers.lima import roi as lima_roi  # noqa: F401
from bliss.common.protocols import CounterContainer
from bliss.common import measurementgroup
from bliss.common.soft_axis import SoftAxis  # noqa
from bliss.common.counter import SoftCounter, Counter  # noqa
from bliss.common.utils import (
    chunk_list,
    custom_error_msg,
    grouped,
    modify_annotations,
    ShellStr,
    shorten_signature,
    typecheck_var_args_pattern,
    typecheck,
)
from bliss.config.conductor.client import get_redis_proxy

from bliss.shell.dialog.helpers import find_dialog, dialog as dialog_dec_cls

# objects given to Bliss shell user
from bliss.common.standard import mv, mvr, mvd, mvdr, move, rockit  # noqa: F401
from bliss.common.cleanup import cleanup, error_cleanup  # noqa: F401

from bliss.common import scans
from bliss.common.scans import *  # noqa: F403
from bliss.scanning.scan import Scan
from bliss.comm.rpc import Client
from bliss.common import logtools
from bliss.common.logtools import elogbook, elog_print  # noqa: F401
from bliss.common.interlocks import interlock_state  # noqa: F401
from blissdata.lima import image_utils as lima_image  # noqa: F401

from bliss.scanning import scan_debug
from bliss.scanning.scan_tools import (  # noqa: F401
    cen,
    com,
    peak,
    trough,
    where,
    find_position,
    fwhm,
)

from bliss.scanning.scan_tools import (
    goto_cen as _goto_cen,
    goto_com as _goto_com,
    goto_peak as _goto_peak,
    goto_min as _goto_min,
    goto_custom as _goto_custom,
    goto_click as _goto_click,
)


from bliss.common.plot import meshselect  # noqa: F401
from bliss.common import plot as plot_module

import tabulate

from typing import Optional, Union
from bliss.controllers.lima.lima_base import Lima
from bliss.common.protocols import Scannable
from bliss.common.types import (  # noqa: F401
    _countable,
    _scannable_or_name,
    _float,
    _scannable_position_list,
    _scannable_position_list_or_group_position_list,
    _providing_channel,
)

from bliss.common.utils import RED
from bliss.common.profiling import time_profile  # noqa: F401
from blisswriter.writer import scan_url_info

############## imports that are only used simplify the
############## shell user access to these functions

# hint: don't forget to add to __all__ as well
from numpy import (
    sin,
    cos,
    tan,
    arcsin,
    arccos,
    arctan,
    arctan2,
    log,
    log10,
    sqrt,
    exp,
    power,
    deg2rad,
    rad2deg,
)
from numpy.random import rand
from time import asctime as date

############## imports for internal usage in this script

from bliss.config import static

##############

__all__ = (
    [
        "wa",
        "wm",
        "wu",
        "sta",
        "stm",
        "mv",
        "umv",
        "mvr",
        "umvr",
        "mvd",
        "umvd",
        "mvdr",
        "umvdr",
        "rockit",
        "move",
        "lsmot",
        "lsconfig",
        "plotinit",
        "plotselect",
        "replot",
        "flint",
        "prdef",
        "sync",
        "lslog",
        "lsdebug",
        "debugon",
        "debugoff",
        "interlock_show",
        "interlock_state",
        "info",
        "bench",
        "clear",
        "metadata_profiling",
        "newproposal",
        "endproposal",
        "newsample",
        "newcollection",
        "newdataset",
        "log_stdout",
        "enddataset",
        "silx_view",
        "pymca",
        "cen",
        "goto_cen",
        "peak",
        "goto_peak",
        "goto_click",
        "trough",
        "goto_min",
        "com",
        "goto_com",
        "where",
        "fwhm",
        "menu",
        "pprint",
        "find_position",
        "goto_custom",
        "time_profile",
        "tw",
        "countdown",
        "show_dialog",
    ]
    + scans.__all__
    + ["elog_print", "elog_add", "elog_plot", "elogbook"]
    + ["print_html", "print_ansi"]
    + [
        "cleanup",
        "error_cleanup",
        "plot",
        "lscnt",
        "lsmg",
        "lsobj",
        "wid",
        "reset_equipment",
    ]
    + ["SoftAxis", "SoftCounter", "edit_roi_counters"]
    + list(limatools.__all__)
    + [
        "sin",
        "cos",
        "tan",
        "arcsin",
        "arccos",
        "arctan",
        "arctan2",
        "log",
        "log10",
        "sqrt",
        "exp",
        "power",
        "deg2rad",
        "rad2deg",
        "rand",
        "sleep",
        "date",
    ]
)

tabulate.PRESERVE_WHITESPACE = True

_ERR = "!ERR"
_DIS = "*DIS*"
_DISABLED = "*DISABLED*"
_MAX_COLS = 9
_MISSING_VAL = "-----"


def _print_errors_with_traceback(errors, device_type="motor"):
    """
    RE-raise caught errors with original traceback
    """
    for (label, error_with_traceback_obj) in errors:
        exc_type, exc_val, exc_tb = error_with_traceback_obj.exc_info
        try:
            # we re-raise in order to pass the motor label to the error msg
            # else calling sys.excepthook(*sys.exc_info()) would be fine
            raise exc_type(
                f"Error on {device_type} '{label}': {str(exc_val)}"
            ).with_traceback(exc_tb)
        except Exception:
            sys.excepthook(*sys.exc_info())


def _tabulate(data, **kwargs):
    kwargs.setdefault("headers", "firstrow")

    return str(tabulate.tabulate(data, **kwargs))


def __row_positions(
    positions: dict[Axis, float], motors: list[Axis], fmts: dict[Axis, str], sep=" "
):
    positions = [format(positions[m], fmts[m]) for m in motors]
    return sep.join(positions)


def __row(cols, fmt, sep=" "):
    return sep.join([format(col, fmt) for col in cols])


def lslog(glob: str = None, debug_only: bool = False):
    """
    Search for loggers.

    It uses a pattern matching normally used by shells.
    Common operators are `*` for any number of characters
    and `?` for one character of any type.

    Args:
        glob: a logger name with optional glob matching
        debug_only: True to display only loggers at debug level
                    (equivalent to lslog)

    Examples:

    >>> lslog()  # prints all loggers

    >>> lslog('*motor?')  # prints loggers that finish with 'motor' + 1 char
                          # like motor1, motor2, motork

    >>> lslog('*Socket*')  # prints loggers that contains 'Socket'

    """
    if glob is None:
        loggers = {
            **global_log._find_loggers("bliss*"),
            **global_log._find_loggers("flint*"),
            **global_log._find_loggers("global*"),
        }
    else:
        loggers = global_log._find_loggers(glob)
    if loggers.items():
        maxlen = max([len(name) for name, _ in loggers.items()])
    else:
        maxlen = 0
    msgfmt = "{0:{width}} {1:8}"
    output = False

    for name in sorted(loggers.keys()):
        logger = loggers[name]
        try:
            has_debug = logger.getEffectiveLevel() == logging.DEBUG
        except AttributeError:
            has_debug = False
        if debug_only and not has_debug:
            continue
        if not output:
            output = True
            print("\n" + msgfmt.format("logger name", "level", width=maxlen))
            print(msgfmt.format("=" * maxlen, 8 * "=", width=maxlen))
        level = logging.getLevelName(logger.getEffectiveLevel())
        if logger.disabled:
            level = "%s [DISABLED]" % level
        print(msgfmt.format(name, level, width=maxlen))
    if output:
        print("")
    else:
        print("No loggers found.\n")


def lsdebug(glob: str = None, debug_only=False) -> None:
    """
    Display current Loggers at DEBUG level
    """
    lslog(glob, debug_only=True)


def debugon(glob_logger_pattern_or_obj) -> None:
    """
    Activate debug-level logging for a specifig logger or an object

    Args:
        glob_logger_pattern_or_obj: glob style pattern matching for logger name, or instance

    Hints on glob: pattern matching normally used by shells
                   common operators are * for any number of characters
                   and ? for one character of any type

    Return:
        None

    Examples:
        >>> log.debugon('*motorsrv')
        Set logger [motorsrv] to DEBUG level
        Set logger [motorsrv.Connection] to DEBUG level
        >>> log.debugon('*rob?')
        Set logger [session.device.controller.roby] to DEBUG level
        Set logger [session.device.controller.robz] to DEBUG level
    """

    if isinstance(glob_logger_pattern_or_obj, str):
        str_arg = glob_logger_pattern_or_obj.lower()
        if str_arg in scan_debug.VALID_DEBUG_MODES:
            current_session.scan_debug_mode = str_arg
            glob_logger_pattern_or_obj = "bliss.scans.debugger"

    activated = global_log.debugon(glob_logger_pattern_or_obj)
    if activated:
        for name in activated:
            print(f"Setting {name} to show debug messages")
    else:
        print(f"NO loggers found for [{glob_logger_pattern_or_obj}]")


def debugoff(glob_logger_pattern_or_obj):

    if isinstance(glob_logger_pattern_or_obj, str):
        str_arg = glob_logger_pattern_or_obj.lower()
        if str_arg in scan_debug.VALID_DEBUG_MODES:
            current_session.scan_debug_mode = None
            glob_logger_pattern_or_obj = "bliss.scans.debugger"

    deactivated = global_log.debugoff(glob_logger_pattern_or_obj)
    if deactivated:
        for name in deactivated:
            print(f"Setting {name} to hide debug messages")
    else:
        print(f"NO loggers found for [{glob_logger_pattern_or_obj}]")


@typecheck
def lscnt(counter_container: typing.Union[CounterContainer, Counter, None] = None):
    """
    Display the list of all counters, sorted alphabetically
    """
    if counter_container is None:
        counters = None
    elif isinstance(counter_container, CounterContainer):
        counters = counter_container.counters
    else:
        # must be Counter
        counters = [counter_container]

    table_info = []
    for counter_name, shape, prefix, name, alias in sorted(iter_counters(counters)):
        if alias:
            alias = "      *"
        table_info.append(itertools.chain([counter_name], (shape, prefix, alias, name)))
    print("")
    print(
        str(
            tabulate.tabulate(
                table_info, headers=["Fullname", "Shape", "Controller", "Alias", "Name"]
            )
        )
    )


def _lsmg():
    """
    Return the list of measurment groups
    Indicate the current active one with a star char: '*'
    """
    active_mg_name = measurementgroup.get_active_name()
    lsmg_str = ""

    for mg_name in measurementgroup.get_all_names():
        if mg_name == active_mg_name:
            lsmg_str += f" * {mg_name}\n"
        else:
            lsmg_str += f"   {mg_name}\n"

    return lsmg_str


def lsmg():
    """
    Print the list of measurment groups
    Indicate the current active one with a star char: '*'
    """
    print(_lsmg())


def lsobj(pattern=None):
    """
    Print the list of BLISS object in current session matching the
    <pattern> string.
    <pattern> can contain jocker characters like '*' or '?'.
    NB: print also badly initilized objects...
    """

    for obj_name in bliss.common.standard._lsobj(pattern):
        print(obj_name, end="  ")

    print("")


def wid():
    """
    Print the list of undulators defined in the session
    and their positions.
    Print all axes of the ID device server.
    """
    print(std_wid())


@typecheck
def stm(*axes: _scannable_or_name, read_hw: bool = False):
    """
    Display state information of the given axes

    Args:
        axis (~bliss.common.axis.Axis): motor axis

    Keyword Args:
        read_hw (bool): If True, force communication with hardware, otherwise
                        (default) use cached value.
    """
    data = iter_axes_state(*axes, read_hw=read_hw)

    table = [(axis, state) for (axis, state) in data]

    print(_tabulate([("Axis", "Status")] + table))

    errors = []
    for label, state in table:
        if str(state) == _ERR:
            errors.append((label, state))

    _print_errors_with_traceback(errors, device_type="motor")


@typecheck
def sta(read_hw: bool = False):
    """
    Return state information about all axes

    Keyword Args:
        read_hw (bool): If True, force communication with hardware, otherwise
                        (default) use cached value.
    """
    return stm(*list(global_map.get_axes_iter()), read_hw=read_hw)


_ERR = "!ERR"
_MAX_COLS = 9
_MISSING_VAL = "-----"


def tw(*motors):
    """
    Display an user interface to move selected motors. (Limited to 5 motors)

    Args:
        motors (~bliss.common.axis.Axis): motor axis

    example:
      DEMO [18]: tw(m0, m1, m2)
    """
    import gevent

    def get_url(timeout=None):
        key = "tweak_ui_" + current_session.name
        redis = get_redis_proxy()

        if timeout is None:
            value = redis.lpop(key)
        else:
            result = redis.blpop(key, timeout=timeout)
            if result is not None:
                key, value = result
                redis.lpush(key, value)
            else:
                value = None

        if value is None:
            raise ValueError(
                "Tweak UI: cannot retrieve Tweak RPC server address from pid "
            )
        url = value.decode().split()[-1]
        return url

    def wait_tweak(tweak):
        while True:
            try:
                tweak.loaded
                break
            except socket.error:
                pass
            gevent.sleep(0.3)

    def create_env():
        from bliss.config.conductor.client import get_default_connection

        beacon = get_default_connection()
        beacon_config = f"{beacon._host}:{beacon._port}"

        env = dict(os.environ)
        env["BEACON_HOST"] = beacon_config
        return env

    if len(motors) > 5:
        raise TypeError("This tool can only display a maximum of 5 motors")

    try:
        with Timeout(10):
            try:
                url = get_url()
            except ValueError:
                pass
            else:
                tweak = Client(url)
                try:
                    tweak.close_new = True
                except socket.error:
                    pass

            tweak = None
            args = f"{sys.executable} -m bliss.shell.qtapp.tweak_ui --session {current_session.name} --motors".split()
            for motor in motors:
                args.append(motor.name)

            process = subprocess.Popen(args, env=create_env())

            try:
                url = get_url(timeout=10)
                tweak = Client(url)
                wait_tweak(tweak)
                connect(tweak, "ct_requested", _tw_ct_requested)
                print("Tweak UI started")
            except Exception:
                process.kill()
                print("Tweak UI launch has failed, please try again")

    except Timeout:
        process.kill()
        raise TimeoutError("The application took too long to start")


def _tw_ct_requested(acq_time, sender):
    ct(acq_time, title="auto_ct")  # noqa: F405


from bliss.shell.dialog.core import show_dialog  # noqa


def wa(**kwargs):
    """
    Display all positions (Where All) in both user and dial units
    """

    max_cols = kwargs.get("max_cols", _MAX_COLS)
    show_dial = kwargs.get("show_dial", True)

    print("Current Positions: user")
    if show_dial:
        print("                   dial")

    header, pos, dial = [], [], []
    if show_dial:
        tables = [(header, pos, dial)]
    else:
        tables = [(header, pos)]
    errors = []

    data = iter_axes_position_all(**kwargs)
    for axis, disabled, error, axis_unit, position, dial_position in data:
        if len(header) == max_cols:
            header, pos, dial = [], [], []
            if show_dial:
                tables.append((header, pos, dial))
            else:
                tables.append((header, pos))

        axis_label = axis.name
        if axis_unit:
            axis_label += "[{0}]".format(axis_unit)

        header.append(axis_label)
        if error:
            errors.append((axis.name, error))
            position = dial_position = _ERR
        if disabled:
            position = dial_position = _DIS
        pos.append(axis.axis_rounder(position))
        dial.append(axis.axis_rounder(dial_position))

        _print_errors_with_traceback(errors, device_type="motor")

    for table in tables:
        print("")
        print(_tabulate(table, disable_numparse=True, stralign="right"))


def wu(**kwargs):
    """
    Display all positions (Where Users) in user units
    """

    wa(show_dial=False, **kwargs)


def lsmot():
    """
    Display names of motors configured in current session.
    """

    motor_list = bliss.common.standard._lsmot()

    # Maximal length of objects names (min 5).
    display_width = shutil.get_terminal_size().columns
    if len(motor_list) == 0:
        max_length = 5
        print("No motor found in current session's config.")
    else:
        max_length = max([len(x) for x in motor_list])

        # Number of items displayable on one line.
        item_number = int(display_width / max_length) + 1

        motor_list.sort(key=str.casefold)

        print("Motors configured in current session:")
        print("-------------------------------------")
        print(tabulate.tabulate(chunk_list(motor_list, item_number), tablefmt="plain"))
        print("\n")


def lsconfig():
    """
    Print all objects found in config.
    Not only objects declared in current session's config.
    """
    obj_dict = dict()

    config = static.get_config()

    # Maximal length of objects names (min 5).
    display_width = shutil.get_terminal_size().columns

    print()

    for name in config.names_list:
        c = config.get_config(name).get("class")
        # print(f"{name}: {c}")
        if c is None and config.get_config(name).plugin == "emotion":
            c = "Motor"
        try:
            obj_dict[c].append(name)
        except KeyError:
            obj_dict[c] = list()
            obj_dict[c].append(name)

    # For each class
    for cc in obj_dict.keys():
        print(f"{cc}: ")
        if cc is None:
            print("----")
        else:
            print("-" * len(cc))
        obj_list = list()

        # put all objects of this class in a list
        while obj_dict[cc]:
            obj_list.append(obj_dict[cc].pop())
        # print(obj_list)

        max_length = max([len(x) for x in obj_list])

        # Number of items displayable on one line.
        item_count = int(display_width / max_length) + 1

        print(tabulate.tabulate(chunk_list(obj_list, item_count), tablefmt="plain"))
        print()


@custom_error_msg(
    TypeError,
    "intended usage: wm(axis1, axis2, ... ) Hint:",
    display_original_msg=True,
)
@shorten_signature(annotations={"axes": "axis1, axis2, ... "}, hidden_kwargs=("kwargs"))
@typecheck
def wm(*axes: _scannable_or_name, **kwargs):
    """
    Display information (position - user and dial, limits) of the given axes

    Args:
        axis: A motor axis

    Example:

    >>> wm(m2, m1, m3)

    .. code-block::

                            m2      m1[mm]       m3
          --------  ----------  ----------  -------
          User
           High     -123.00000   128.00000      inf
           Current   -12.00000     7.00000  3.00000
           Low       456.00000  -451.00000     -inf
          Offset       0.00000     3.00000  0.00000
          Dial
           High      123.00000   123.00000      inf
           Current    12.00000     2.00000  3.00000
           Low      -456.00000  -456.00000     -inf
    """
    if not axes:
        print(
            "wm() needs at least one axis name/object as parameter.\n"
            "example: wm(mot1)\n"
            "         wm(mot1, mot2, ... motN)"
        )
        return

    max_cols = kwargs.get("max_cols", _MAX_COLS)
    err = kwargs.get("err", _ERR)

    errors = []
    header = [""]
    User, high_user, user, low_user = (
        ["User~~~~"],
        ["~High~~~"],
        ["~Current"],
        ["~Low~~~~"],
    )
    Dial, high_dial, dial, low_dial = (
        ["Dial~~~~"],
        ["~High~~~"],
        ["~Current"],
        ["~Low~~~~"],
    )
    Offset, Spacer = ["Offset~~"], [""]
    tables = [
        (
            header,
            User,
            high_user,
            user,
            low_user,
            Offset,
            Spacer,
            Dial,
            high_dial,
            dial,
            low_dial,
        )
    ]

    for wm_info in iter_axes_position(*axes, **kwargs):

        if len(header) == max_cols:
            header = [None]
            User, high_user, user, low_user = (
                ["User~~~~"],
                ["~High~~~"],
                ["~Current"],
                ["~Low~~~~"],
            )
            Dial, high_dial, dial, low_dial = (
                ["Dial~~~~"],
                ["~High~~~"],
                ["~Current"],
                ["~Low~~~~"],
            )
            Offset = ["Offset~~"]
            tables.append(
                (
                    header,
                    User,
                    high_user,
                    user,
                    low_user,
                    Offset,
                    Spacer,
                    Dial,
                    high_dial,
                    dial,
                    low_dial,
                )
            )
        axis_label = wm_info.axis.name
        if wm_info.unit:
            axis_label += "[{0}]".format(wm_info.unit)

        if wm_info.user_high_limit not in (None, err):
            user_high_limit = wm_info.axis.axis_rounder(wm_info.user_high_limit)
            dial_high_limit = wm_info.axis.axis_rounder(wm_info.dial_high_limit)
        else:
            user_high_limit = dial_high_limit = _MISSING_VAL

        if wm_info.user_low_limit not in (None, err):
            user_low_limit = wm_info.axis.axis_rounder(wm_info.user_low_limit)
            dial_low_limit = wm_info.axis.axis_rounder(wm_info.dial_low_limit)
        else:
            user_low_limit = dial_low_limit = _MISSING_VAL

        high_user.append(user_high_limit)
        user_position = wm_info.user_position
        dial_position = wm_info.dial_position
        if wm_info.error:
            errors.append((wm_info.axis.name, wm_info.error))
            user_position = dial_position = _ERR
        elif wm_info.disabled:
            axis_label += f" {_DISABLED}"
        user_position = wm_info.axis.axis_rounder(user_position)
        dial_position = wm_info.axis.axis_rounder(dial_position)
        header.append(axis_label)
        User.append(None)
        user.append(user_position)
        low_user.append(user_low_limit)
        Dial.append(None)
        high_dial.append(dial_high_limit)
        dial.append(dial_position)
        low_dial.append(dial_low_limit)
        offset = wm_info.axis.axis_rounder(wm_info.offset)
        Offset.append(offset)

    _print_errors_with_traceback(errors, device_type="motor")

    for table in tables:
        print("")
        print(
            _tabulate(table, disable_numparse=True, stralign="right").replace("~", " ")
        )


@custom_error_msg(
    TypeError,
    "intended usage: umv(motor1, target_position_1, motor2, target_position_2, ... )",
    display_original_msg=False,
)
@modify_annotations({"args": "motor1, pos1, motor2, pos2, ..."})
@typecheck_var_args_pattern([Scannable, _float])
def umv(*args):
    """
    Move given axes to given absolute positions providing updated display of
    the motor(s) position(s) while it(they) is(are) moving.

    Arguments are interleaved axis and respective absolute target position.
    """
    _umove(list(grouped(args, 2)))


@custom_error_msg(
    TypeError,
    "intended usage: umvr(motor1, relative_displacement_1, motor2, relative_displacement_2, ... )",
    display_original_msg=False,
)
@modify_annotations({"args": "motor1, rel. pos1, motor2, rel. pos2, ..."})
@typecheck_var_args_pattern([Scannable, _float])
def umvr(*args):
    """
    Move given axes to given relative positions providing updated display of
    the motor(s) position(s) while it(they) is(are) moving.

    Arguments are interleaved axis and respective relative target position.
    """
    _umove(list(grouped(args, 2)), relative=True)


@custom_error_msg(
    TypeError,
    "intended usage: umvd(motor1, target_position_1, motor2, target_position_2, ... )",
    display_original_msg=False,
)
@modify_annotations({"args": "motor1, pos1, motor2, pos2, ..."})
@typecheck_var_args_pattern([Scannable, _float])
def umvd(*args):
    """
    Move given axes to given absolute dial positions providing updated display of
    the motor(s) user position(s) while it(they) is(are) moving.

    Arguments are interleaved axis and respective absolute target position.
    """
    _umove(list(grouped(args, 2)), dial=True)


@custom_error_msg(
    TypeError,
    "intended usage: umvdr(motor1, relative_displacement_1, motor2, relative_displacement_2, ... )",
    display_original_msg=False,
)
@modify_annotations({"args": "motor1, rel. pos1, motor2, rel. pos2, ..."})
@typecheck_var_args_pattern([Scannable, _float])
def umvdr(*args):
    """
    Move given axes to given relative dial positions providing updated display of
    the motor(s) user position(s) while it(they) is(are) moving.

    Arguments are interleaved axis and respective relative target position.
    """
    _umove(list(grouped(args, 2)), relative=True, dial=True)


@typecheck
@shorten_signature(hidden_kwargs=[])
def goto_cen(
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
):
    """
    Return the motor position corresponding to the center of the fwhm of the last scan.
    Move scanned motor to this value.
    If <counter> is not specified, use selected counter.

    Example: goto_cen()
    """
    return _goto_cen(counter=counter, axis=axis, scan=scan, move=_umove)


@typecheck
@shorten_signature(hidden_kwargs=[])
def goto_com(
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
):
    """
    Return center of mass of last scan according to <counter>.
    Move scanned motor to this value.
    If <counter> is not specified, use selected counter.

    Example: goto_com(diode2)
    """
    return _goto_com(counter=counter, axis=axis, scan=scan, move=_umove)


@typecheck
@shorten_signature(hidden_kwargs=[])
def goto_peak(
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
):
    """
    Return position of scanned motor at maximum of <counter> of last scan.
    Move scanned motor to this value.
    If <counter> is not specified, use selected counter.

    Example: goto_peak()
    """
    return _goto_peak(counter=counter, axis=axis, scan=scan, move=_umove)


@typecheck
@shorten_signature(hidden_kwargs=[])
def goto_min(
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
):
    """
    Return position of scanned motor at minimum of <counter> of last scan.
    Move scanned motor to this value.
    If <counter> is not specified, use selected counter.
    """
    return _goto_min(counter=counter, axis=axis, scan=scan, move=_umove)


@typecheck
def goto_custom(
    func: Callable[[Any, Any], float],
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
):
    return _goto_custom(func=func, counter=counter, axis=axis, scan=scan, move=_umove)


def goto_click(scatter=False, curve=False):
    """Move the motor displayed by Flint at the location clicked by the user.

    It supports both curves and scatters, based on the previous scan done by BLISS.

    - For a curve, the x-axis have to display a BLISS motor
    - For a scatter, both x and y axes have to be a BLISS motor

    If both `scatter` and `curve` are false (the default) the last scan is used
    to decide which plot have to be used.

    Arguments:
        scatter: If true, use the default scatter plot
        curve: If true, use the default scatter plot

    Raises:
        RuntimeError: If flint was not open or displayed plot was not properly setup.
    """
    return _goto_click(scatter=scatter, curve=curve, move=_umove)


def _max_value_length(axis: Axis) -> int:
    """Returns the max size the axis value can take"""
    umin, umax = axis.limits
    dmin, dmax = axis.dial_limits

    def integer_digits(value):
        """Measure the size of the integer + negsign"""
        text = f"{value:f}"
        return text.find(".")

    values = [umin, umax, dmin, dmax]
    values = [integer_digits(v) for v in values]
    max_size = max(values)

    digits = axis.display_digits
    if digits != 0:
        max_size += digits + 1  # the dot and the digits

    return max_size


def _umove(axis_pos_list: _scannable_position_list_or_group_position_list, **kwargs):
    kwargs["wait"] = False
    group, motor_pos = _move(axis_pos_list, **kwargs)
    motors = list(group.axes_with_reals.values())
    with error_cleanup(group.stop):
        motor_names = list()
        max_value_len: list[int] = []

        for axis in motors:
            display_name = global_map.alias_or_name(axis)
            if axis.unit:
                display_name += f"[{axis.unit}]"
            motor_names.append(display_name)

            max_value_len.append(len(display_name))
            max_value_len.append(_max_value_length(axis))

        col_len = max(max(max_value_len), 8)

        hfmt = f"^{col_len}"
        axes_value_format: dict[Axis, str] = {}
        for axis in motors:
            axes_value_format[axis] = f">{col_len}.0{axis.display_digits}f"
        print("")
        first_row = __row(motor_names, hfmt, sep="  ")
        row_len = len(first_row)
        print(first_row.rjust(row_len + 5))
        print("\n")
        magic_char = "\033[F"  # "back to previous line" character

        def format_group(group):
            positions = group.position_with_reals
            dials = group.dial_with_reals
            user_pos = __row_positions(positions, motors, axes_value_format, sep="  ")
            dial_pos = __row_positions(dials, motors, axes_value_format, sep="  ")
            row = f"user {user_pos}\ndial {dial_pos}\n"
            ret_depth = magic_char * row.count("\n")
            return f"{ret_depth}{row}"

        previous_line = None
        while group.is_moving:
            previous_line = format_group(group)
            print(previous_line, end="", flush=True)
            sleep(0.1)

        try:
            # Ensure the GroupMove move task has finished before returning.
            # This is important for the eventual pseudo motors, linked to
            # some axes of this Group, to be properly updated before this
            # function returns.
            group.wait_move()
        finally:
            # print last time for final positions
            last_line = format_group(group)
            if previous_line != last_line:
                print(last_line, end="", flush=True)
            print("")

    return group, motor_pos


def __pyhighlight(code, bg="dark", outfile=None):
    formatter = TerminalFormatter(bg=bg)
    return highlight(code, PythonLexer(), formatter, outfile=outfile)


def get_source_code(obj_or_name):
    """
    Return source code for an object, either by passing the object or its name in the current session env dict
    """
    is_arg_str = isinstance(obj_or_name, str)
    if is_arg_str:
        obj, name = current_session.env_dict[obj_or_name], obj_or_name
    else:
        obj = obj_or_name
        name = None
    try:
        real_name = obj.__name__
    except AttributeError:
        real_name = str(obj)
    if name is None:
        name = real_name

    if (
        inspect.ismodule(obj)
        or inspect.isclass(obj)
        or inspect.istraceback(obj)
        or inspect.isframe(obj)
        or inspect.iscode(obj)
    ):
        pass
    elif callable(obj):
        obj = inspect.unwrap(obj)
    else:
        try:
            obj = type(obj)
        except Exception:
            pass

    try:
        fname = inspect.getfile(obj)
    except TypeError:
        return f"Source code for {repr(obj)} is not available.", []
    lines, line_nb = inspect.getsourcelines(obj)

    if name == real_name or is_arg_str:
        header = "'{0}' is defined in:\n{1}:{2}\n".format(name, fname, line_nb)
    else:
        header = "'{0}' is an alias for '{1}' which is defined in:\n{2}:{3}\n".format(
            name, real_name, fname, line_nb
        )

    return header, lines


def prdef(obj_or_name):
    """
    Show the text of the source code for an object or the name of an object.
    """
    header, lines = get_source_code(obj_or_name)
    print(header)
    print_formatted_text(
        ANSI(__pyhighlight("".join(lines))), output=current_session._pt_output
    )


@typecheck
def plotinit(*counters: _providing_channel):
    """
    Select counters to plot and to use only with the next scan command.

    User-level function built on top of bliss.common.scans.plotinit()
    """

    # If called without arguments, prints help.
    if not counters:
        print(
            """
plotinit usage:
    plotinit(<counters>*)                  - Select a set of counters

example:
    plotinit(counter1, counter2)
    plotinit('*')                          - Select everything
    plotinit('beamviewer:roi_counters:*')  - Select all the ROIs from a beamviewer
    plotinit('beamviewer:*_sum')           - Select any sum ROIs from a beamviewer
"""
        )
    else:
        plot_module.plotinit(*counters)
    print("")

    names = plot_module.get_next_plotted_counters()
    if names:
        print("Plotted counter(s) for the next scan:")
        for cnt_name in names:
            print(f"- {cnt_name}")
    else:
        print("No specific counter(s) for the next scan")
    print("")


@typecheck
def plotselect(*counters: _providing_channel):
    """
    Select counters to plot and used by alignment functions (cen, peak, etc).

    User-level function built on top of bliss.common.plot.plotselect()
    """

    all_counters_names = [x.name for x in iter_counters()] + [
        x.fullname for x in iter_counters()
    ]

    # If called without arguments, prints help.
    if not counters:
        print(
            """
plotselect usage:
    plotselect(<counters>*)                  - Select a set of counters

example:
    plotselect(counter1, counter2)
    plotselect('*')                          - Select everything
    plotselect('beamviewer:roi_counters:*')  - Select all the ROIs from a beamviewer
    plotselect('beamviewer:*_sum')           - Select any sum ROIs from a beamviewer
"""
        )
    else:
        if len(counters) == 1 and counters[0] is None:
            counters = []

        # If counter is provided as a string, warn if it does not exist.
        for counter in counters:
            if isinstance(counter, str):
                if counter not in all_counters_names:
                    print(f"WARNING: '{counter}' is not a valid counter")

        plot_module.plotselect(*counters)
    print("")
    print(
        "Plotted counter(s) last selected with plotselect (could be different from the current display):"
    )
    for cnt_name in plot_module.get_plotted_counters():
        if cnt_name in all_counters_names:
            print(f"- {cnt_name}")
        else:
            print("- " + RED(f"{cnt_name}"))
    print("")


def replot():
    """Clear any user marker from the default curve plot"""
    plot_module.replot()


def flint():
    """
    Return a proxy to the running Flint application used by BLISS, else create
    one.

    If there is problem to create or to connect to Flint, an exception is
    raised.

        # This can be used to start Flint
        BLISS [1]: flint()

        # This can be used to close Flint
        BLISS [1]: f = flint()
        BLISS [2]: f.close()

        # This can be used to kill Flint
        BLISS [1]: f = flint()
        BLISS [2]: f.kill9()
    """
    proxy = plot_module.get_flint(creation_allowed=True, mandatory=True)
    print("Current Flint PID: ", proxy.pid)
    print("")
    return proxy


@typecheck
def edit_roi_counters(detector: Lima, acq_time: Optional[float] = None):
    """
    Edit the given detector ROI counters.

    When called without arguments, it will use the image from specified detector
    from the last scan/ct as a reference. If `acq_time` is specified,
    it will do a `ct()` with the given count time to acquire a new image.


    .. code-block:: python

        # Flint will be open if it is not yet the case
        edit_roi_counters(pilatus1, 0.1)

        # Flint must already be open
        ct(0.1, pilatus1)
        edit_roi_counters(pilatus1)
    """
    return detector.edit_rois(acq_time)


def interlock_show(wago_obj=None):
    """
    Display interlocks configuration on given Wago object (if given)
    or display configuration of all known Wagos
    """
    if wago_obj:
        wago_obj.interlock_show()
    else:
        try:
            wago_instance_list = tuple(
                global_map[id_]["instance"]()
                for id_ in global_map.find_children("wago")
            )
        except TypeError:
            print("No Wago found")
            return
        names = [wago.name for wago in wago_instance_list]
        print_formatted_text(
            HTML(f"Currently configured Wagos: <violet>{' '.join(names)}</violet>\n\n"),
            output=current_session._pt_output,
        )
        for wago in wago_instance_list:
            wago.interlock_show()


def menu(obj=None, dialog_type: str = None, *args, **kwargs):
    """
    Display a dialog for acting on the object if this is implemented

    Args:
        obj: the object on which you want to operate, if no object is provided
             a complete list of available objects that have implemented some
             dialogs will be displayed.
        dialog_type: the dialog type that you want to display between one
             of the available. If this parameter is omitted and only one dialog
             is available for the given object than that dialog is diplayed,
             if instead more than one dialog is available will be launched a
             first selection dialog to choose from availables and than the
             selected one.

    Examples:

    >>> menu()  # will display all bliss objects that have dialog implemented

    >>> menu(wba)  # will launch the only available dialog for wba: "selection"

    >>> menu(wba, "selection")  # same as previous

    >>> menu(lima_simulator)  # will launch a selection dialog between available
    >>>                       # choices and than the selected one
    """
    if obj is None:
        names = set()
        # remove (_1, _2, ...) ptpython shell items that create false positive
        env = {
            k: v for (k, v) in current_session.env_dict.items() if not k.startswith("_")
        }

        for key, obj in env.items():
            try:
                # intercepts functions like `ascan`
                if obj.__name__ in dialog_dec_cls.DIALOGS.keys():
                    names.add(key)
            except AttributeError:
                try:
                    # intercept class instances like `wago_simulator`
                    if obj.__class__.__name__ in dialog_dec_cls.DIALOGS.keys():
                        names.add(key)

                except AttributeError:
                    pass

        return ShellStr(
            "Dialog available for the following objects:\n\n" + "\n".join(sorted(names))
        )
    dialog = find_dialog(obj)
    if dialog is None:
        return ShellStr("No dialog available for this object")
    try:
        return dialog(dialog_type)
    except ValueError as exc:
        logtools.log_error(dialog, "Error while execution the dialog", exc_info=True)
        return ShellStr(str(exc))


@contextlib.contextmanager
def bench():
    """
    Context manager for basic timing of procedure, this has to be use like this:
        with bench():
            <command>
    example:
        with bench():
             mot1._hw_position
    gives:
        Execution time: 2ms 119μs

    """
    start_time = time.perf_counter()
    yield
    duration = time.perf_counter() - start_time

    print(f"Execution time: {timedisplay.duration_format(duration)}")


def clear():
    """
    Clear terminal screen
    """
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")


# Metadata gathering profiling


def metadata_profiling(**kw):
    from bliss.scanning.scan_meta import get_user_scan_meta, get_controllers_scan_meta
    from bliss.shell.formatters.table import IncrementalTable

    user_perf = get_user_scan_meta()._profile_metadata_gathering(**kw)
    ctrl_perf = get_controllers_scan_meta()._profile_metadata_gathering(**kw)

    head = [
        "name",
        "category",
        "metadata gathering time (ms)",
    ]

    def nan_sort_key(tpl):
        if numpy.isnan(tpl[2]):
            return -numpy.inf
        return tpl[2]

    for title, perf in [
        ("USER META DATA", user_perf),
        ("CONTROLLERS META DATA", ctrl_perf),
    ]:
        lmargin = "  "
        tab = IncrementalTable([head], col_sep="|", flag="", lmargin=lmargin)
        for (name, catname, dt) in sorted(perf, key=nan_sort_key, reverse=True):
            tab.add_line([name, catname, dt * 1000])
        tab.resize(16, 60)
        tab.add_separator("-", line_index=1)

        w = tab.full_width
        txt = f"\n{lmargin}{'='*w}\n{lmargin}{title:^{w}}\n{lmargin}{'='*w}\n\n"
        txt += f"{tab}\n\n"
        print(txt)


# Data Policy
# from bliss/scanning/scan_saving.py


@typecheck
@elogbook.disable_command_logging
def newproposal(
    proposal_name: Optional[str] = None,
    session_name: Optional[str] = None,
    prompt: Optional[bool] = False,
):
    """
    Change the proposal and session name used to determine the saving path.
    """
    current_session.scan_saving.newproposal(
        proposal_name, session_name=session_name, prompt=prompt
    )


@typecheck
@elogbook.disable_command_logging
def newsample(collection_name: Optional[str] = None, description: Optional[str] = None):
    """
    Same as `newcollection` with sample name equal to the collection name.
    """
    current_session.scan_saving.newsample(collection_name, description=description)


@typecheck
@elogbook.disable_command_logging
def newcollection(
    collection_name: Optional[str] = None,
    sample_name: Optional[str] = None,
    sample_description: Optional[str] = None,
):
    """
    Change the collection name used to determine the saving path.
    Metadata can be modified later if needed.
    """
    current_session.scan_saving.newcollection(
        collection_name, sample_name=sample_name, sample_description=sample_description
    )


@typecheck
@elogbook.disable_command_logging
def newdataset(
    dataset_name: Optional[Union[str, int]] = None,
    description: Optional[str] = None,
    sample_name: Optional[str] = None,
    sample_description: Optional[str] = None,
):
    """
    Change the dataset name used to determine the saving path.

    The description can be modified until the dataset is closed.
    """
    current_session.scan_saving.newdataset(
        dataset_name,
        description=description,
        sample_name=sample_name,
        sample_description=sample_description,
    )


@elogbook.disable_command_logging
def endproposal():
    """
    Close the active dataset and move to the default inhouse proposal.
    """
    current_session.scan_saving.endproposal()


@elogbook.disable_command_logging
def enddataset():
    """
    Close the active dataset.
    """
    current_session.scan_saving.enddataset()


# Silx


@typecheck
def silx_view(scan: typing.Union[Scan, int, None] = None):
    """
    Open silx view on a given scan. When no scan is given it
    opens the current data file.
    """
    uris = None
    if scan is None:
        uris = [current_session.scan_saving.filename]
    elif isinstance(scan, int):
        try:
            scan_obj = current_session.scans[scan]
        except IndexError:
            pass
        else:
            uris = scan_url_info.scan_urls(scan_obj.scan_info)
    else:
        uris = scan_url_info.scan_urls(scan.scan_info)
    _launch_silx(uris)


def _launch_silx(uris: typing.Union[typing.List[str], None] = None):
    args = f"{sys.executable} -m silx.app.view.main".split()
    if uris:
        args.extend(uris)
    return subprocess.Popen(args, start_new_session=True)


# PyMCA


@typecheck
def pymca(scan: typing.Union[Scan, None] = None):
    """
    Open PyMCA on a given scan (default last scan)
    """

    filename = None
    try:
        if scan is None:
            scan = current_session.scans[-1]
        filename = scan._scan_info["filename"]
    except IndexError:
        pass
    _launch_pymca(filename)


def _launch_pymca(filename: typing.Union[str, None] = None):
    args = f"{sys.executable} -m PyMca5.PyMcaGui.pymca.PyMcaMain".split()
    if filename:
        args.append(filename)
    return subprocess.Popen(args, start_new_session=True)


def print_html(text, **kwargs):
    """
    Print formatted text as HTML (see prompt-toolkit 'print_formatted_text')
    """
    return current_session.env_dict["__print_html"](text, **kwargs)


def print_ansi(text, **kwargs):
    """
    Print formatted text with ANSI escape sequences (see prompt-toolkit 'print_formatted_text')
    """
    return current_session.env_dict["__print_ansi"](text, **kwargs)


@elogbook.disable_command_logging
def elog_add(index=-1, beamline_only: Optional[bool] = None):
    """
    Send to the logbook given cell output and the print that was
    performed during the elaboration.
    Only a fixed size of output are kept in memory (normally last 20).

    Args:
        index (int): Index of the cell to be sent to logbook, can
                     be positive reflecting the prompt index
                     or negative (relative to the current cell).
                     Default is -1 (previous cell)

    Example:
        BLISS [2]: diode
          Out [2]: 'diode` counter info:
                     counter type = sampling
                     sampling mode = MEAN
                     fullname = simulation_diode_sampling_controller:diode
                     unit = None
                     mode = MEAN (1)

        BLISS [3]: elog_add()  # sends last output from diode
    """
    return current_session.env_dict["__elog_add"](index, beamline_only)


def elog_plot(controller=None):
    """Export the actual curve plot to the logbook

    Arguments:
        controller: If specified, a Lima or MCA controller can be specified
                    to export the relative specific plot
    """
    flint = plot_module.get_flint(creation_allowed=False, mandatory=False)
    if flint is None:
        print("Flint is not available or not reachable")
        return
    flint.wait_end_of_scans()
    if controller is None:
        p = flint.get_live_plot(kind="default-curve")
    elif isinstance(controller, Lima):
        p = flint.get_live_plot(controller)
    elif isinstance(controller, BaseMCA):
        p = flint.get_live_plot(controller)
    else:
        raise RuntimeError(
            "Reaching plot from controller type {type(controller)} is not supported"
        )
    try:
        p.export_to_logbook()
    except RuntimeError as e:
        print(e.args[0])


def countdown(duration_s, message="Waiting...", end_message=None):
    """
    Wait <duration_s> seconds while printing a countdown message.
    If provided, print <end_message> once the countdown is finished.
    Ex: countdown(2, 'waiting for refill', 'Gooooo !')
    """
    starting_time = time.time()
    remaining_s = duration_s
    print(f"\033[0G{message} {remaining_s:4d} s", end="")

    remaining_s = int(duration_s - (time.time() - starting_time) + 1)

    while remaining_s > 0:
        print(f"\033[0G{message} {remaining_s:4d} s", end="")
        time.sleep(0.1)
        remaining_s = int(duration_s - (time.time() - starting_time) + 1)

    print(f"\033[0G{message} {0:4d} s")
    if end_message:
        print(end_message)


def log_stdout(fdir=None, fname=None):
    """Duplicate BLISS shell output into specified file "<fdir>/<fname>".

    If 'fname' is not specified, a default file name is automatically generated as follow:
        * No data policy: "<session>_<date>.log"
        * ESRF data policy: "<beamline>_<session>_<date>_<proposal>.log"

        Note: during a session, if <date> or <proposal> change, the logging file path is updated.

    <fdir> and <fname> are stored as persitant settings, so that logging is automatically re-activated
    at next session if it has been enabled once.

    Usage examples:

        * log_stdout(): show current logging status and file path

        * log_stdout("/tmp/logging"): enable logging and set file directory to "/tmp/logging".
          The default file name will be used.

        * log_stdout(False): disable stdout logging (clear )

        * log_stdout(fname='log.txt'): specify a custom logging file name (a file directory must have been specified first)

        * log_stdout(fname=''): enable usage of the default file name

    """
    from bliss.shell.cli import repl

    br = repl.BlissRepl()  # bliss repl singleton
    if fdir is None and fname is None:
        br.show_stdout_file()
    elif fdir is False:
        br.disable_stdout_file()
    else:
        if fdir is not None:
            if not os.path.isabs(fdir):
                raise ValueError("directory path must be absolute")
            if not os.path.isdir(fdir):
                raise ValueError(f"directory '{fdir}' does not exist")
        br.enable_stdout_file(fdir, fname)
