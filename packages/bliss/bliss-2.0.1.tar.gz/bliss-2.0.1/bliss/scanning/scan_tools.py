import numpy
from typing import Optional, Callable, Any
from bliss import current_session, global_map
from bliss.common.protocols import Scannable
from bliss.common.types import _countable
from bliss.common.plot import display_motor
from bliss.scanning.scan import Scan
from bliss.scanning.scan_display import ScanDisplay
from bliss.common.utils import shorten_signature, typecheck
from bliss.common.plot import get_flint
from bliss.common.logtools import log_warning
from bliss.common.motor_group import Group
from bliss.common.cleanup import error_cleanup, axis as cleanup_axis

"""
Alignment Helpers: cen peak com that interact with plotselect
and work outside of the context of a scan while interacting
with the last scan.
"""


@typecheck
def get_counter(counter_name: str):
    """
    Gets a counter instance from a counter name
    """
    for _counter in global_map.get_counters_iter():
        if _counter.fullname == counter_name:
            return _counter
    raise RuntimeError("Can't find the counter")


def get_selected_counter_name(counter=None) -> str:
    """
    Returns the name of the counter selected.

    That's one of the counters actually selected by `plotselect`. It does not
    mean the counter is actually displayed by Flint.

    Returns ONLY ONE counter.

    Raises RuntimeError if more than one counter is selected.

    Used to determine which counter to use for cen pic curs functions.
    """

    if not current_session.scans:
        raise RuntimeError("Scans list is empty!")
    scan_counter_names = set(current_session.scans[-1].streams.keys())

    scan_display = ScanDisplay()
    selected_counter_names = scan_display.displayed_channels
    alignment_counts = scan_counter_names.intersection(selected_counter_names)

    if not alignment_counts:
        # fall-back plan ... check if there is only one counter in the scan
        alignment_counts2 = {
            c
            for c in scan_counter_names
            if (":elapsed_time" not in c and ":epoch" not in c and "axis:" not in c)
        }
        if len(alignment_counts2) == 1:
            print(f"using {next(iter(alignment_counts2))} for calculation")
            alignment_counts = alignment_counts2
        else:
            raise RuntimeError(
                "No counter selected...\n"
                "Hints: Use flint or plotselect to define which counter to use for alignment"
            )
    elif len(alignment_counts) > 1:
        if counter is None:
            raise RuntimeError(
                "There is actually several counter selected (%s).\n"
                "Only one should be selected.\n"
                "Hints: Use flint or plotselect to define which counter to use for alignment"
                % alignment_counts
            )
        if counter.name in alignment_counts:
            return counter.name
        else:
            raise RuntimeError(
                f"Counter {counter.name} is not part of the last scan.\n"
            )
    counter_name = alignment_counts.pop()

    # Display warning on discrepancy with Flint
    flint = get_flint(mandatory=False, creation_allowed=False)
    if flint is not None:
        flint_selected_names = None
        try:
            plot = flint.get_live_scan("default-curve")
            if plot is not None:
                flint_selected_names = plot.displayed_channels
        except Exception:
            pass
        else:
            if flint_selected_names is None or counter_name not in flint_selected_names:
                log_warning(
                    "The used counter name '%s' is not actually displayed in Flint",
                    counter_name,
                )
            elif counter_name in flint_selected_names and len(flint_selected_names) > 1:
                log_warning(
                    "The used counter name '%s' is not the only one displayed in Flint",
                    counter_name,
                )

    return counter_name


def last_scan_motors():
    """
    Return a list of motor used in the last scan.

    It includes direct motors (the one explicitly requested in the scan) and
    indirect motors used to compute the position of pseudo motors.
    """
    if not len(current_session.scans):
        raise RuntimeError("No scan available.")
    scan = current_session.scans[-1]

    return scan._get_data_axes(include_calc_reals=True)


def _scan_calc(
    func, counter=None, axis=None, scan=None, marker=True, goto=False, move=None
):
    if counter is None:
        counter = get_counter(get_selected_counter_name())
    if scan is None:
        scan = current_session.scans[-1]
    if callable(func):
        res = scan.find_position(func, counter, axis=axis, return_axes=True)
        func = func.__name__  # for label managment
    else:
        res = getattr(scan, func)(counter, axis=axis, return_axes=True)
    if marker:
        clear_markers()
        for ax, value in res.items():
            display_motor(
                ax,
                scan=scan,
                position=value,
                label=func + "\n" + str(value),
                marker_id=func,
            )

            if ax in ["elapsed_time", "epoch"]:
                continue

            # display current position if in scan range
            scan_dat = scan.streams[ax][:]
            if (
                not goto
                and ax.position < numpy.max(scan_dat)
                and ax.position > numpy.min(scan_dat)
            ):
                display_motor(
                    ax,
                    scan=scan,
                    position=ax.position,
                    label="\n\ncurrent\n" + str(ax.position),
                    marker_id="current",
                )
    if goto:
        scan._goto_multimotors(res, move=move)
        display_motor(
            ax,
            scan=scan,
            position=ax.position,
            label="\n\ncurrent\n" + str(ax.position),
            marker_id="current",
        )
        return
    elif len(res) == 1:
        return next(iter(res.values()))
    else:
        return res


@typecheck
@shorten_signature(hidden_kwargs=[])
def fwhm(
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
):
    """
    Return Full Width at Half of the Maximum of previous scan according to <counter>.
    If <counter> is not specified, use selected counter.

    Example: f = fwhm()
    """
    return _scan_calc("fwhm", counter=counter, axis=axis, scan=scan, marker=False)


@typecheck
@shorten_signature(hidden_kwargs=[])
def cen(
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
):
    """
    Return the motor position corresponding to the center of the fwhm of the last scan.
    If <counter> is not specified, use selected counter.

    Example: cen(diode3)
    """
    return _scan_calc("cen", counter=counter, axis=axis, scan=scan)


@typecheck
def find_position(
    func: Callable[[Any, Any], float],
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
):
    return _scan_calc(func, counter=counter, axis=axis, scan=scan)


@typecheck
@shorten_signature(hidden_kwargs=[])
def goto_cen(
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
    move: Optional[Callable] = None,
):
    """
    Return the motor position corresponding to the center of the fwhm of the last scan.
    Move scanned motor to this value.
    If <counter> is not specified, use selected counter.

    Example: goto_cen()

    Arguments:
        move: Standard move command to be used
    """
    return _scan_calc(
        "cen", counter=counter, axis=axis, scan=scan, goto=True, move=move
    )


@typecheck
@shorten_signature(hidden_kwargs=[])
def com(
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
):
    """
    Return center of mass of last scan according to <counter>.
    If <counter> is not specified, use selected counter.

    Example: scan_com = com(diode2)
    """
    return _scan_calc("com", counter=counter, axis=axis, scan=scan)


@typecheck
@shorten_signature(hidden_kwargs=[])
def goto_com(
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
    move: Optional[Callable] = None,
):
    """
    Return center of mass of last scan according to <counter>.
    Move scanned motor to this value.
    If <counter> is not specified, use selected counter.

    Example: goto_com(diode2)

    Arguments:
        move: Standard move command to be used
    """
    return _scan_calc(
        "com", counter=counter, axis=axis, scan=scan, goto=True, move=move
    )


@typecheck
@shorten_signature(hidden_kwargs=[])
def peak(
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
):
    """
    Return position of scanned motor at maximum of <counter> of last scan.
    If <counter> is not specified, use selected counter.

    Example: max_of_scan = peak()
    """
    return _scan_calc("peak", counter=counter, axis=axis, scan=scan)


@typecheck
@shorten_signature(hidden_kwargs=[])
def goto_peak(
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
    move: Optional[Callable] = None,
):
    """
    Return position of scanned motor at maximum of <counter> of last scan.
    Move scanned motor to this value.
    If <counter> is not specified, use selected counter.

    Example: goto_peak()

    Arguments:
        move: Standard move command to be used
    """
    return _scan_calc(
        "peak", counter=counter, axis=axis, scan=scan, goto=True, move=move
    )


@typecheck
@shorten_signature(hidden_kwargs=[])
def trough(
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
):
    """
    Return position of scanned motor at minimum of <counter> of last scan.
    If <counter> is not specified, use selected counter.

    Example: min_of_scan = min()

    Arguments:
        move: Standard move command to be used
    """
    return _scan_calc("trough", counter=counter, axis=axis, scan=scan)


@typecheck
@shorten_signature(hidden_kwargs=[])
def goto_min(
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
    move: Optional[Callable] = None,
):
    """
    Return position of scanned motor at minimum of <counter> of last scan.
    Move scanned motor to this value.
    If <counter> is not specified, use selected counter.

    Example: goto_min()
    """
    return _scan_calc(
        "trough", counter=counter, axis=axis, scan=scan, goto=True, move=move
    )


@typecheck
def goto_custom(
    func: Callable[[Any, Any], float],
    counter: Optional[_countable] = None,
    axis: Optional[Scannable] = None,
    scan: Optional[Scan] = None,
    move: Optional[Callable] = None,
):
    return _scan_calc(func, counter=counter, axis=axis, scan=scan, goto=True, move=move)


def where():
    """
    Draw a vertical line on the plot at current position of scanned motor.

    Example: where()
    """
    for axis in last_scan_motors():
        display_motor(
            axis, marker_id="current", label="\n\ncurrent\n" + str(axis.position)
        )


def clear_markers():
    for axis in last_scan_motors():
        display_motor(axis, marker_id="cen", position=numpy.nan)
        display_motor(axis, marker_id="peak", position=numpy.nan)
        display_motor(axis, marker_id="com", position=numpy.nan)
        display_motor(axis, marker_id="current", position=numpy.nan)


def goto_click(scatter=False, curve=False, move=None):
    """Move the motor displayed by Flint at the location clicked by the user.

    It supports both curves and scatters, based on the previous scan done by BLISS.

    - For a curve, the x-axis have to display a BLISS motor
    - For a scatter, both x and y axes have to be a BLISS motor

    If both `scatter` and `curve` are false (the default) the last scan is used
    to decide which plot have to be used.

    Arguments:
        scatter: If true, use the default scatter plot
        curve: If true, use the default scatter plot
        move: Standard move command to be used

    Raises:
        RuntimeError: If flint was not open or displayed plot was not properly setup.
    """
    f = get_flint(creation_allowed=False, mandatory=False)
    if f is None:
        raise RuntimeError("Flint was not started")

    if not scatter and not curve:
        session = current_session
        scans = session.scans
        if not scans:
            raise RuntimeError("No scan available; Need to do a scan first!")
        scan = scans[-1]

        scatter_plot = False
        plots = scan.scan_info.get("plots", [])
        if isinstance(plots, list):
            for plot_info in plots:
                kind = plot_info.get("kind")
                if kind == "scatter-plot":
                    scatter_plot = True
                    break
    elif scatter:
        scatter_plot = True
    else:
        scatter_plot = False

    if scatter_plot:
        p = f.get_live_plot("default-scatter")
        position = p.select_points(1)

        axis_1_name = p.xaxis_channel_name
        axis_2_name = p.yaxis_channel_name
        if axis_1_name is None or axis_2_name is None:
            raise RuntimeError("One of scatter axis is not defined")
        if not axis_1_name.startswith("axis:") or not axis_2_name.startswith("axis:"):
            raise RuntimeError("One of scatter axis is not a motor")
        axis_1_name = axis_1_name.split(":", 1)[-1]
        axis_2_name = axis_2_name.split(":", 1)[-1]
        axis1 = session.env_dict[axis_1_name]
        axis2 = session.env_dict[axis_2_name]

        axis_1_pos, axis_2_pos = position[0]
        goto = {axis1: axis_1_pos, axis2: axis_2_pos}
        with error_cleanup(
            *goto.keys(), restore_list=(cleanup_axis.POS,), verbose=True
        ):
            if move is not None:
                move(goto, wait=True, relative=False)
            else:
                group = Group(*goto.keys())
                group.move(goto, wait=True, relative=False)

        # FIXME: Display a motor marker in the scatter plot
    else:
        p = f.get_live_plot("default-curve")
        position = p.select_points(1)
        axis_pos = position[0][0]

        axis_name = p.xaxis_channel_name
        if axis_name is None:
            raise RuntimeError("One of scatter axis is not defined")
        if not axis_name.startswith("axis:"):
            raise RuntimeError("Can't find an axis on plot")
        axis_name = axis_name.split(":", 1)[-1]

        axis = session.env_dict[axis_name]
        goto = {axis: axis_pos}
        with error_cleanup(
            *goto.keys(), restore_list=(cleanup_axis.POS,), verbose=True
        ):
            if move is not None:
                move(goto, wait=True, relative=False)
            else:
                group = Group(*goto.keys())
                group.move(goto, wait=True, relative=False)

        display_motor(
            axis, marker_id="current", label="\n\ncurrent\n" + str(axis.position)
        )
