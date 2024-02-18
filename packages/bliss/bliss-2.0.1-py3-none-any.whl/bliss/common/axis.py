# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Axis related classes (:class:`~bliss.common.axis.Axis`, \
:class:`~bliss.common.axis.AxisState`, :class:`~bliss.common.axis.Motion`
and :class:`~bliss.common.axis.GroupMove`)
"""

from __future__ import annotations

from bliss import global_map
from bliss.common.deprecation import deprecated_warning
from bliss.common.hook import execute_pre_move_hooks
from bliss.common.protocols import HasMetadataForDataset, Scannable
from bliss.common.cleanup import capture_exceptions
from bliss.common.motor_config import MotorConfig
from bliss.common.motor_settings import AxisSettings
from bliss.common import event
from bliss.common.utils import with_custom_members, safe_get
from bliss.config.channels import Channel
from bliss.common.logtools import log_debug, log_warning, log_error
from bliss.common.utils import rounder
from bliss.common.utils import autocomplete_property
from bliss.comm.exceptions import CommunicationError
from bliss.common.closed_loop import ClosedLoop

import enum
import gevent
import gevent.event
import gevent.lock
import re
import math
import functools
import collections
import contextlib
import itertools
import numbers
import numpy
import warnings

warnings.simplefilter("once", DeprecationWarning)


#: Default polling time
DEFAULT_POLLING_TIME = 0.02


class AxisOnLimitError(RuntimeError):
    pass


class AxisOffError(RuntimeError):
    pass


class AxisFaultError(RuntimeError):
    pass


def float_or_inf(value, inf_sign=1):
    if value is None:
        value = float("inf")
        sign = math.copysign(1, inf_sign)
    else:
        sign = 1
    value = float(value)  # accepts float or numpy array of 1 element
    return sign * value


def _prepare_one_controller_motions(controller, motions):
    try:
        return controller.prepare_all(*motions)
    except NotImplementedError:
        # this is to "clear" the exception
        # (see issue #3294)
        pass
    for motion in motions:
        controller.prepare_move(motion)


def _start_one_controller_motions(controller, motions):
    try:
        return controller.start_all(*motions)
    except NotImplementedError:
        # this is to "clear" the exception
        # (see issue #3294)
        pass
    for motion in motions:
        controller.start_one(motion)


def _stop_one_controller_motions(controller, motions):
    try:
        return controller.stop_all(*motions)
    except NotImplementedError:
        # this is to "clear" the exception
        # (see issue #3294)
        pass
    for motion in motions:
        controller.stop(motion.axis)


def _emit_move_done(obj, value=True, from_channel=False):
    try:
        if not from_channel:
            # this is used by calculation motors controllers,
            # to distinguish between 'move_done' received via
            # channel update, or when an actual move with the
            # local move loop is done
            event.send_safe(obj, "internal_move_done", value)
    finally:
        # this is the event, any subscriber can register, to
        # know when a move is done
        event.send_safe(obj, "move_done", value)


class GroupMove:
    def __init__(self, parent=None):
        self.parent = parent
        self._move_task = None
        self._motions_dict = {}
        self._stop_motion = None
        self._interrupted_move = False
        self._backlash_started_event = gevent.event.Event()
        self._move_started_event = gevent.event.Event()
        self._end_of_move_event = gevent.event.Event()

    # Public API
    @property
    def motions_iter(self):
        return itertools.chain.from_iterable(self._motions_dict.values())

    @property
    def is_moving(self):
        return any(motion.axis.is_moving for motion in self.motions_iter)

    def _fill_motions_dict(self, motions_dict, axis_pos_dict, relative, polling_time):
        """Feed motions_dict passed as parameter from the { axis: pos } dictionary, with
        motion objects organised by controller: { controller: [motion, ...], ... }

        This is a recursive function, filling motions_dict will with all
        motions from top pseudos to bottom hardware axes (see issue #1388).

        axes with None motion (i.e. already in place) are store in motions_dict[None]
        """
        from bliss.controllers.motor import CalcController

        motions_by_controller = {}
        all_motions = set()

        # Fill motions_by_controller with Motion objects corresponding
        # to the given axis_pos_dict, stored by controller.
        # Also, fill motions_dict[None] with None-Motion axes
        for axis, target_pos in axis_pos_dict.items():
            motion = axis.get_motion(
                target_pos, relative=relative, polling_time=polling_time
            )
            # motion can be None if axis is not supposed to move
            if motion is None:
                motions_dict.setdefault(None, set()).add(axis)
            else:
                motions_by_controller.setdefault(axis.controller, []).append(motion)
                all_motions.add(motion)

        # Now fill motions_dict with the per_controller motions found above
        # and if controller is a CalcController obtain the "axis_pos_dict" of its reals.
        # Then call _fill_motions_dict again, passing the reals "axis_pos_dict".
        # The recursion finishes when hitting the bottom axes (hardware axes).
        for controller, motions in motions_by_controller.items():
            motions_dict.setdefault(controller, []).extend(motions)
            if isinstance(controller, CalcController):
                # get motions of reals (taking into account effect of params axes)
                real_move_dict = controller._get_real_axes_move_dict(
                    motions
                    + [
                        motion
                        for motion in all_motions
                        if motion.axis in controller.params
                    ]
                )

                # The reals of this controller can also be CalcAxis.
                # So call _fill_motions_dict passing these reals.
                # This recursion ends when there is no more CalcAxis in
                # sub-layers. At the end of the recursion, all CalcAxis
                # and Axis motions will be identified and stored in motions_dict.
                self._fill_motions_dict(
                    motions_dict,
                    real_move_dict,
                    relative=False,
                    polling_time=polling_time,
                )

    def _filter_motions_dict(self, motions_dict):

        # Remove the list of physical axes with a None motion from motions_dict
        # and store them in excluded_axes for a later usage.
        excluded_axes = set()
        for axis in motions_dict.pop(None, ()):
            excluded_axes.add(axis)

            # Different combinations of {pseudo pos, calc params}
            # can lead to the same position of the reals. So reals won't move
            # and won't update pseudos positions via Louie callbacks.
            # So send "internal_position" signal on reals to force linked pseudos to update their positions.
            event.send(axis, "internal_position", axis.position)

        # Analyse motions_dict and check if a CalcAxis motion should be discarded because
        # all of its reals don t have a motion (i.e. included in excluded_axes).
        # If a CalcAxis is discarded, perform the analysis again
        # until all unnecessary motions have been removed.
        while self._find_motion_to_delete(motions_dict, excluded_axes):
            pass

    def _find_motion_to_delete(self, motions_dict, excluded_axes):
        from bliss.controllers.motor import CalcController

        for controller, motions in list(motions_dict.items()):
            if isinstance(controller, CalcController):
                if not set(controller.reals) - excluded_axes:
                    excluded_axes |= {motion.axis for motion in motions}
                    del motions_dict[controller]
                    return True

    def move(
        self,
        axis_pos_dict,
        prepare_motion,
        start_motion,
        stop_motion,
        move_func=None,
        relative=False,
        wait=True,
        polling_time=None,
    ):

        # ============ NOTES ABOUT MOTION PRINCIPLES ==================================================

        # 1) _fill_motion_dict:
        #    - Obtain motion objects ordered by controller for all axes involved in the move,
        #      including Reals of CalcAxis, down to physical axes.
        #    - CalcAxis.get_motion always return a motion object (even if already in place)
        #    - Axis.get_motion returns None if already_in_place

        # 2) _filter_motions_dict: handle CalcAxis specificities
        #    - force position update of CalcAxis linked to physical axes with a None motion
        #    - remove motion of CalcAxis which have no Reals motions (Reals could be CalcAxis too)
        #    - del controller key of motions_dict if it has no motions at all

        # 3) cancel move if motions_dict is empty after the filtering

        # 4) for remaining motions:
        #    - motion.axis._set_position = motion.user_target_pos
        #    - motion.axis._set_moving_state() (on Axis and CalcAxis)
        #    - spawn move_task and link task's end to _end_of_move() callback
        #    - _end_of_move() calls axis._set_move_done()  (on Axis only!)
        #    - Axis._set_move_done(), emit signal "internal_move_done" and "move_done"
        #    - "internal_move_done" triggers the _real_axis_move_done() callback on the CalcController
        #    - _set_moving_state() is called on pseudos only if all its reals are not moving

        motions_dict = {}
        self._fill_motions_dict(motions_dict, axis_pos_dict, relative, polling_time)
        self._filter_motions_dict(motions_dict)

        if motions_dict:
            self.start(
                motions_dict,
                prepare_motion,
                start_motion,
                stop_motion,
                move_func=move_func,
                wait=wait,
                polling_time=polling_time,
            )

    def start(
        self,
        motions_dict,
        prepare_motion,
        start_motion,
        stop_motion,
        move_func=None,
        wait=True,
        polling_time=None,
    ):
        # motions_dict contains filtered motions indexed by controller (can be CalcAxis and/or Axis)
        self._motions_dict = motions_dict
        self._stop_motion = stop_motion
        self._interrupted_move = False
        self._move_started_event.clear()
        self._backlash_started_event.clear()

        all_motions = list(self.motions_iter)
        for motion in all_motions:
            motion.axis._group_move = self

        with execute_pre_move_hooks(all_motions):
            for axis in (m.axis for m in all_motions):
                axis._check_ready()

        for controller, motions in self._motions_dict.items():
            if prepare_motion is not None:
                prepare_motion(controller, motions)

        # set target position and moving state
        for motion in all_motions:
            target_pos = motion.user_target_pos
            if target_pos is not None:
                motion.axis._set_position = target_pos

            msg = motion.user_msg
            if msg:
                event.send_safe(motion.axis, "msg", msg)

            motion.axis._set_moving_state()

        if self.parent:
            _emit_move_done(self.parent, value=False)

        self._move_task = gevent.spawn(
            self._move, prepare_motion, start_motion, stop_motion, move_func
        )
        self._move_task.link(self._end_of_move)

        # Wait if necessary and raise the move task exception if any
        if wait:
            self.wait()

    def wait(self):
        if self._move_task is not None:
            try:
                self._move_task.get()
            except BaseException:
                self.stop(wait=False)
                raise
            finally:
                self._end_of_move_event.wait()

                if self._interrupted_move:
                    for motion in self.motions_iter:
                        _axis = motion.axis
                        _axis_pos = safe_get(_axis, "position", on_error="!ERR")
                        _axis_pos = _axis.axis_rounder(_axis_pos)
                        event.send_safe(
                            _axis,
                            "msg",
                            f"Axis {_axis.name} stopped at position {_axis_pos}",
                        )

    def stop(self, wait=True):
        if self._move_task:
            self._interrupted_move = True
            self._move_task.kill(block=False)

        if wait:
            self.wait()

    # Internal methods

    def _monitor_move(self, motions_dict, move_func, stop_func):
        monitor_move_tasks = {}

        for controller, motions in motions_dict.items():
            for motion in motions:
                if isinstance(motion.axis, CalcAxis):
                    # calc axes will get updated via real motors updates
                    continue
                if move_func is None:
                    move_func = "_handle_move"
                task = gevent.spawn(getattr(motion.axis, move_func), motion)
                monitor_move_tasks[task] = motion

        try:
            gevent.joinall(monitor_move_tasks, raise_error=True)
        except BaseException:
            # in case of error, all moves are stopped
            # _stop_move is called with the same monitoring tasks:
            # the stop command will be sent, then the same monitoring continues
            # in '_stop_move'
            self._stop_move(motions_dict, stop_func, monitor_move_tasks)
            raise

    def _stop_move(self, motions_dict, stop_motion, stop_wait_tasks=None, wait=True):
        self._interrupted_move = True

        stop_tasks = []
        for controller, motions in motions_dict.items():
            stop_tasks.append(gevent.spawn(stop_motion, controller, motions))

        with capture_exceptions(raise_index=0) as capture:
            # wait for all stop commands to be sent
            with capture():
                gevent.joinall(stop_tasks, raise_error=True)
            if capture.failed:
                gevent.joinall(stop_tasks)

            if wait:
                if stop_wait_tasks is None:
                    # create tasks to wait for end of motion
                    stop_wait_tasks = {}
                    for controller, motions in motions_dict.items():
                        for motion in motions:
                            stop_wait_tasks[
                                gevent.spawn(motion.axis._handle_move, motion)
                            ] = motion

                # wait for end of motion
                gevent.joinall(stop_wait_tasks)

    def _do_backlash_move(self, motions_dict):
        backlash_motions = collections.defaultdict(list)
        for controller, motions in motions_dict.items():
            for motion in motions:
                if motion.backlash:
                    backlash_motions[controller].append(motion.backlash_motion)

        if backlash_motions:
            backlash_mv_group = GroupMove()
            backlash_mv_group._do_move(
                backlash_motions,
                _start_one_controller_motions,
                _stop_one_controller_motions,
                None,
                self._backlash_started_event,
            )

    def _do_move(
        self, motions_dict, start_motion, stop_motion, move_func, started_event
    ):
        for controller, motions in motions_dict.items():
            for motion in motions:
                motion.last_state = None

        with capture_exceptions(raise_index=0) as capture:
            # Spawn start motion tasks for all controllers
            start = [
                gevent.spawn(start_motion, controller, motions)
                for controller, motions in motions_dict.items()
            ]

            # wait for start tasks to be all done ;
            # in case of error or if wait is interrupted (ctrl-c, kill...),
            # immediately stop and return
            with capture():
                gevent.joinall(start, raise_error=True)
            if capture.failed:
                # either a start task failed, or ctrl-c or kill happened.
                # First, let all start task to finish
                # /!\ it is important to join those, to ensure stop is called
                # after tasks are done otherwise there is a risk 'end' is
                # called before 'start' is all done
                gevent.joinall(start)
                # then, stop all axes and wait end of motion
                self._stop_move(motions_dict, stop_motion)
                # exit
                return

            # All controllers are now started
            started_event.set()

            # Spawn the monitoring for all motions
            with capture():
                self._monitor_move(motions_dict, move_func, stop_motion)

    def _end_of_move(self, _=None):
        all_motions = list(self.motions_iter)
        hooks = collections.defaultdict(list)
        for motion in all_motions:
            for hook in motion.axis.motion_hooks:
                hooks[hook].append(motion)
        # the exit stack will ensure all hooks are executed (in reverse order),
        # even in case of error
        try:
            with contextlib.ExitStack() as final_tasks:
                if self.parent:
                    final_tasks.callback(_emit_move_done, self.parent)

                for axis in (m.axis for m in all_motions):
                    if not isinstance(axis, CalcAxis):
                        final_tasks.callback(axis._set_move_done)

                for hook, motions in list(hooks.items()):
                    final_tasks.callback(hook.post_move, motions)
        finally:
            self._end_of_move_event.set()

    def _move(self, prepare_motion, start_motion, stop_motion, move_func):
        try:
            all_motions = list(self.motions_iter)
            with capture_exceptions(raise_index=0) as capture:
                # if anything fails, exception will raise ;
                # the moving state will be restored and move task
                # will exit
                with capture():
                    self._do_move(
                        self._motions_dict,
                        start_motion,
                        stop_motion,
                        move_func,
                        self._move_started_event,
                    )

                if not self._interrupted_move:
                    # Do backlash move, if needed
                    with capture():
                        self._do_backlash_move(self._motions_dict)

                reset_setpos = bool(capture.failed) or self._interrupted_move

                # cleanup
                # -------
                # update set position if motor has been stopped,
                # or if an exception happened or if motion type is
                # home search or hw limit search ;
                # as state update happened just before, this
                # is equivalent to sync_hard -> emit the signal
                # (useful for real motor positions update in case
                # of pseudo axis)
                # -- jog move is a special case
                if len(all_motions) == 1:
                    motion = all_motions[0]
                    if motion.type == "jog":
                        reset_setpos = False
                        motion.axis._jog_cleanup(
                            motion.saved_velocity, motion.reset_position
                        )
                    elif motion.type == "homing":
                        reset_setpos = True
                    elif motion.type == "limit_search":
                        reset_setpos = True

                if reset_setpos:
                    with capture():
                        for motion in all_motions:
                            motion.axis._set_position = motion.axis.position
                            event.send(motion.axis, "sync_hard")

                # once move task is finished, check encoder if needed
                with capture():
                    with contextlib.ExitStack() as read_encoders:
                        for axis in (m.axis for m in all_motions):
                            if axis._check_encoder:
                                read_encoders.callback(axis._do_encoder_reading)
        finally:
            # "link" callbacks can be executed a bit after the end
            # of the greenlet, so we deactivate the callback and
            # we call "set_move_done" to ensure it gets called
            # without delay. If the greenlet never runs (because it
            # is killed just after "start" with wait=False for example),
            # the link will still ensure "set_move_done" is called
            self._move_task.unlink(self._end_of_move)
            self._end_of_move()


class Modulo:
    def __init__(self, mod=360):
        self.modulo = mod

    def __call__(self, axis):
        dial_pos = axis.dial
        axis._Axis__do_set_dial(dial_pos % self.modulo)


class Motion:
    """Motion information

    Represents a specific motion. The following members are present:

    * *axis* (:class:`Axis`): the axis to which this motion corresponds to
    * *target_pos* (:obj:`float`): final motion position
    * *delta* (:obj:`float`): motion displacement
    * *backlash* (:obj:`float`): motion backlash

    Note: target_pos and delta can be None, in case of specific motion
    types like homing or limit search
    """

    def __init__(
        self,
        axis,
        target_pos,
        delta,
        motion_type="move",
        target_name=None,
    ):
        self.__axis = axis
        self.__type = motion_type
        self.__target_name = target_name
        self._target_pos = target_pos
        self.delta = delta
        self.backlash = 0
        self._polling_time = None

    @property
    def axis(self):
        """Reference to :class:`Axis`"""
        return self.__axis

    @property
    def type(self):
        return self.__type

    @property
    def target_name(self):
        """Descriptive text about target position: home+, lim-, ..."""
        return self.__target_name

    @property
    def dial_target_pos(self):
        try:
            return self._target_pos / self.axis.steps_per_unit
        except TypeError:
            pass

    @property
    def user_target_pos(self):
        return self.axis.dial2user(self.dial_target_pos)

    @property
    def target_pos(self):
        """Return the target position corresponding to the first move in case of backlash,
        or corresponding to the target_pos if there is no backlash"""
        return self._target_pos - self.backlash

    @target_pos.setter
    def target_pos(self, new_target_pos):
        """Set the new target pos, in steps, for this Motion

        Note: if there is backlash, the returned .target_pos will be for the first move
        """
        self._target_pos = new_target_pos

    @property
    def backlash_motion(self):
        """Return the Motion object corresponding to the final move, if there is backlash"""
        return Motion(self.axis, self._target_pos, self.backlash)

    @property
    def user_msg(self):
        start_ = self.__axis.axis_rounder(self.axis.position)
        if self.type == "jog":
            msg = (
                f"Moving {self.axis.name} from {start_} until it is stopped, at constant velocity in {'positive' if self.delta > 0 else 'negative'} direction: {abs(self.dial_target_pos)}\n"
                f"To stop it: {self.axis.name}.stop()"
            )
            return msg

        else:
            if self.target_name:
                # can be a string in case of special move like limit search, homing...
                end_ = self.target_name
            else:
                if self.user_target_pos is None:
                    return
                end_ = self.__axis.axis_rounder(self.user_target_pos)
            return f"Moving {self.axis.name} from {start_} to {end_}"

    @property
    def polling_time(self):
        return (
            self._polling_time
            if self._polling_time is not None
            else self.axis._polling_time
        )

    @polling_time.setter
    def polling_time(self, new_polling_time):
        self._polling_time = new_polling_time


class Trajectory:
    """Trajectory information

    Represents a specific trajectory motion.

    """

    def __init__(self, axis, pvt):
        """
        Args:
            axis -- axis to which this motion corresponds to
            pvt  -- numpy array with three fields ('position','velocity','time')
        """
        self.__axis = axis
        self.__pvt = pvt
        self._events_positions = numpy.empty(
            0, dtype=[("position", "f8"), ("velocity", "f8"), ("time", "f8")]
        )

    @property
    def axis(self):
        return self.__axis

    @property
    def pvt(self):
        return self.__pvt

    @property
    def events_positions(self):
        return self._events_positions

    @events_positions.setter
    def events_positions(self, events):
        self._events_positions = events

    def has_events(self):
        return self._events_positions.size

    def __len__(self):
        return len(self.pvt)

    def convert_to_dial(self):
        """
        Return a new trajectory with pvt position, velocity converted to dial units and steps per unit
        """
        user_pos = self.__pvt["position"]
        user_velocity = self.__pvt["velocity"]
        pvt = numpy.copy(self.__pvt)
        pvt["position"] = self._axis_user2dial(user_pos) * self.axis.steps_per_unit
        pvt["velocity"] = user_velocity * self.axis.steps_per_unit
        new_obj = self.__class__(self.axis, pvt)
        pattern_evts = numpy.copy(self._events_positions)
        pattern_evts["position"] *= self.axis.steps_per_unit
        pattern_evts["velocity"] *= self.axis.steps_per_unit
        new_obj._events_positions = pattern_evts
        return new_obj

    def _axis_user2dial(self, user_pos):
        return self.axis.user2dial(user_pos)


class CyclicTrajectory(Trajectory):
    def __init__(self, axis, pvt, nb_cycles=1, origin=0):
        """
        Args:
            axis -- axis to which this motion corresponds to
            pvt  -- numpy array with three fields ('position','velocity','time')
                    point coordinates are in relative space
        """
        super(CyclicTrajectory, self).__init__(axis, pvt)
        self.nb_cycles = nb_cycles
        self.origin = origin

    @property
    def pvt_pattern(self):
        return super(CyclicTrajectory, self).pvt

    @property
    def events_pattern_positions(self):
        return super(CyclicTrajectory, self).events_positions

    @events_pattern_positions.setter
    def events_pattern_positions(self, values):
        self._events_positions = values

    @property
    def is_closed(self):
        """True if the trajectory is closed (first point == last point)"""
        pvt = self.pvt_pattern
        return (
            pvt["time"][0] == 0
            and pvt["position"][0] == pvt["position"][len(self.pvt_pattern) - 1]
        )

    @property
    def pvt(self):
        """Return the full PVT table. Positions are absolute"""
        pvt_pattern = self.pvt_pattern
        if self.is_closed:
            # take first point out because it is equal to the last
            raw_pvt = pvt_pattern[1:]
            cycle_size = raw_pvt.shape[0]
            size = self.nb_cycles * cycle_size + 1
            offset = 1
        else:
            raw_pvt = pvt_pattern
            cycle_size = raw_pvt.shape[0]
            size = self.nb_cycles * cycle_size
            offset = 0
        pvt = numpy.empty(size, dtype=raw_pvt.dtype)
        last_time, last_position = 0, self.origin
        for cycle in range(self.nb_cycles):
            start = cycle_size * cycle + offset
            end = start + cycle_size
            pvt[start:end] = raw_pvt
            pvt["time"][start:end] += last_time
            last_time = pvt["time"][end - 1]
            pvt["position"][start:end] += last_position
            last_position = pvt["position"][end - 1]

        if self.is_closed:
            pvt["time"][0] = pvt_pattern["time"][0]
            pvt["position"][0] = pvt_pattern["position"][0] + self.origin

        return pvt

    @property
    def events_positions(self):
        pattern_evts = self.events_pattern_positions
        time_offset = 0.0
        last_time = self.pvt_pattern["time"][-1]
        nb_pattern_evts = len(pattern_evts)
        all_events = numpy.empty(
            self.nb_cycles * len(pattern_evts), dtype=pattern_evts.dtype
        )
        for i in range(self.nb_cycles):
            sub_evts = all_events[
                i * nb_pattern_evts : i * nb_pattern_evts + nb_pattern_evts
            ]
            sub_evts[:] = pattern_evts
            sub_evts["time"] += time_offset
            time_offset += last_time
        return all_events

    def _axis_user2dial(self, user_pos):
        # here the trajectory is relative to the origin so the **pvt_pattern**
        # should not contains the axis offset as it's already in **origin**
        return user_pos * self.axis.sign

    def convert_to_dial(self):
        """
        Return a new trajectory with pvt position, velocity converted to dial units and steps per unit
        """
        new_obj = super(CyclicTrajectory, self).convert_to_dial()
        new_obj.origin = self.axis.user2dial(self.origin) * self.axis.steps_per_unit
        new_obj.nb_cycles = self.nb_cycles
        return new_obj


def lazy_init(func):
    @functools.wraps(func)
    def func_wrapper(self, *args, **kwargs):
        if self.disabled:
            raise RuntimeError(f"Axis {self.name} is disabled")
        try:
            self.controller._initialize_axis(self)
        except Exception as e:
            if isinstance(e, CommunicationError):
                # also disable the controller
                self.controller._disabled = True
            self._disabled = True
            raise
        else:
            if not self.controller.axis_initialized(self):
                # failed to initialize
                self._disabled = True
        return func(self, *args, **kwargs)

    return func_wrapper


@with_custom_members
class Axis(Scannable, HasMetadataForDataset):
    """
    This class is typically used by motor controllers in bliss to export
    axis with harmonised interface for users and configuration.
    """

    class READ_POSITION_MODE(enum.Enum):
        CONTROLLER = 1
        ENCODER = 2

    def __init__(self, name, controller, config):
        self.__name = name
        self.__controller = controller
        self.__move_done = gevent.event.Event()
        self.__move_done_callback = gevent.event.Event()
        self.__move_done.set()
        self.__move_done_callback.set()
        self.__motion_hooks = []
        for hook in config.get("motion_hooks", []):
            hook._add_axis(self)
            self.__motion_hooks.append(hook)
        self.__encoder = config.get("encoder")
        if self.__encoder is not None:
            self.__encoder.axis = self
        self.__config = MotorConfig(config)
        self.__settings = AxisSettings(self)
        self._init_config_properties()
        self.__no_offset = False
        self._group_move = GroupMove()
        self._lock = gevent.lock.Semaphore()
        self.__positioner = True
        self._disabled = False
        if config.get("closed_loop"):
            self._closed_loop = ClosedLoop(self)
        else:
            self._closed_loop = None

        self._display_digits = None

        try:
            config.parent
        except AttributeError:
            # some Axis don't have a controller, e.g. SoftAxis
            disabled_cache = list()
        else:
            disabled_cache = config.parent.get(
                "disabled_cache", []
            )  # get it from controller (parent)
        disabled_cache.extend(config.get("disabled_cache", []))  # get it for this axis
        for setting_name in disabled_cache:
            self.settings.disable_cache(setting_name)

        # self.config ?
        self._unit = self.config.get("unit", str, None)
        self._polling_time = config.get("polling_time", DEFAULT_POLLING_TIME)
        global_map.register(self, parents_list=["axes", controller])

        # create Beacon channels
        self.settings.init_channels()
        self._move_stop_channel = Channel(
            f"axis.{self.name}.move_stop",
            default_value=False,
            callback=self._external_stop,
            self_updates=False,
        )
        self._jog_velocity_channel = Channel(
            f"axis.{self.name}.change_jog_velocity",
            default_value=None,
            callback=self._set_jog_velocity,
            self_updates=False,
        )

    def __close__(self):
        self.close()

    def close(self):
        self.controller.close()

    def axis_rounder(self, value):
        """
        Return a rounded value of <value> as a string.
        Use `display_digits` as number of digits after decimal point.
        Use `bliss.common.utils.rounder` function to perform the rounding.
        <value> : number
        """

        if not isinstance(value, numbers.Number):
            return value

        if math.isnan(value):
            return value

        # Convert a number of digits to a model string usable by rounder() function.
        # ex: 2 -> 0.01 ; 8 -> 0.00000001
        try:
            display_model = float(
                f"{1/pow(10,self.display_digits):0.{self.display_digits}f}"
            )
        except ValueError as val_err:
            raise RuntimeError(
                f"axis {self.name}: error on display_digits:{self.display_digits} {type(self.display_digits)}"
            ) from val_err

        # print("display_model=", display_model)
        rounded_pos_str = rounder(display_model, value)
        return rounded_pos_str

    @property
    def _check_encoder(self):
        return self.config.get("check_encoder", bool, self.encoder) and self.encoder

    @property
    def _read_position_mode(self):
        if self.config.get("read_position", str, "controller") == "encoder":
            return self.READ_POSITION_MODE.ENCODER
        else:
            return self.READ_POSITION_MODE.CONTROLLER

    @property
    def _encoder_read_mode(self):
        return self._read_position_mode == self.READ_POSITION_MODE.ENCODER

    @property
    def no_offset(self):
        return self.__no_offset

    @no_offset.setter
    def no_offset(self, value):
        self.__no_offset = value

    @property
    def unit(self):
        """unit used for the Axis (mm, deg, um...)"""
        return self._unit

    @property
    def name(self):
        """name of the axis"""
        return self.__name

    @property
    def _positioner(self):
        """Axis positioner"""
        return self.__positioner

    @_positioner.setter
    def _positioner(self, new_p):
        self.__positioner = new_p

    @autocomplete_property
    def controller(self):
        """
        Motor controller of the axis
        Reference to :class:`~bliss.controllers.motor.Controller`
        """
        return self.__controller

    @property
    def config(self):
        """Reference to the :class:`~bliss.common.motor_config.MotorConfig`"""
        return self.__config

    @property
    def settings(self):
        """
        Reference to the
        :class:`~bliss.controllers.motor_settings.AxisSettings`
        """
        return self.__settings

    @property
    def is_moving(self):
        """
        Tells if the axis is moving (:obj:`bool`)
        """
        return not self.__move_done.is_set()

    def _init_config_properties(
        self, velocity=True, acceleration=True, limits=True, sign=True, backlash=True
    ):
        self.__steps_per_unit = self.config.get("steps_per_unit", float, 1)
        self.__tolerance = self.config.get("tolerance", float, 1e-4)
        if velocity:
            if "velocity" in self.settings.config_settings:
                self.__config_velocity = self.config.get("velocity", float)
            if "jog_velocity" in self.settings.config_settings:
                self.__config_jog_velocity = self.config.get(
                    "jog_velocity", float, self.__config_velocity
                )
            self.__config_velocity_low_limit = self.config.get(
                "velocity_low_limit", float, float("inf")
            )
            self.__config_velocity_high_limit = self.config.get(
                "velocity_high_limit", float, float("inf")
            )
        if acceleration:
            if "acceleration" in self.settings.config_settings:
                self.__config_acceleration = self.config.get("acceleration", float)
        if limits:
            self.__config_low_limit = self.config.get("low_limit", float, float("-inf"))
            self.__config_high_limit = self.config.get(
                "high_limit", float, float("+inf")
            )
        if backlash:
            self.__config_backlash = self.config.get("backlash", float, 0)

    @property
    def steps_per_unit(self):
        """Current steps per unit (:obj:`float`)"""
        return self.__steps_per_unit

    @property
    def config_backlash(self):
        """Current backlash in user units (:obj:`float`)"""
        return self.__config_backlash

    @property
    @lazy_init
    def backlash(self):
        """Current backlash in user units (:obj:`float`)"""
        backlash = self.settings.get("backlash")
        if backlash is None:
            return 0
        return backlash

    @backlash.setter
    def backlash(self, backlash):
        self.settings.set("backlash", backlash)

    @property
    @lazy_init
    def closed_loop(self):
        """
        Closed loop object associated to axis.
        """
        return self._closed_loop

    @property
    def tolerance(self):
        """Current Axis tolerance in dial units (:obj:`float`)"""
        return self.__tolerance

    @property
    def encoder(self):
        """
        Reference to :class:`~bliss.common.encoder.Encoder` or None if no
        encoder is defined
        """
        return self.__encoder

    @property
    def motion_hooks(self):
        """Registered motion hooks (:obj:`MotionHook`)"""
        return self.__motion_hooks

    @property
    @lazy_init
    def offset(self):
        """Current offset in user units (:obj:`float`)"""
        offset = self.settings.get("offset")
        if offset is None:
            return 0
        return offset

    @offset.setter
    def offset(self, new_offset):
        if self.no_offset:
            raise RuntimeError(
                f"{self.name}: cannot change offset, axis has 'no offset' flag"
            )
        self.__do_set_position(offset=new_offset)

    @property
    @lazy_init
    def sign(self):
        """Current motor sign (:obj:`int`) [-1, 1]"""
        sign = self.settings.get("sign")
        if sign is None:
            return 1
        return sign

    @sign.setter
    @lazy_init
    def sign(self, new_sign):
        new_sign = float(
            new_sign
        )  # works both with single float or numpy array of 1 element
        new_sign = math.copysign(1, new_sign)
        if new_sign != self.sign:
            if self.no_offset:
                raise RuntimeError(
                    f"{self.name}: cannot change sign, axis has 'no offset' flag"
                )
            self.settings.set("sign", new_sign)
            # update pos with new sign, offset stays the same
            # user pos is **not preserved** (like spec)
            self.position = self.dial2user(self.dial)

    def set_setting(self, *args):
        """Sets the given settings"""
        self.settings.set(*args)

    def get_setting(self, *args):
        """Return the values for the given settings"""
        return self.settings.get(*args)

    def has_tag(self, tag):
        """
        Tells if the axis has the given tag

        Args:
            tag (str): tag name

        Return:
            bool: True if the axis has the tag or False otherwise
        """
        for t, axis_list in self.__controller._tagged.items():
            if t != tag:
                continue
            if self.name in [axis.name for axis in axis_list]:
                return True
        return False

    @property
    def disabled(self):
        return self._disabled

    def enable(self):
        self._disabled = False
        self.hw_state  # force update

    @lazy_init
    def on(self):
        """Turns the axis on"""
        if self.is_moving:
            return

        self.__controller.set_on(self)
        state = self.__controller.state(self)
        self.settings.set("state", state)

    @lazy_init
    def off(self):
        """Turns the axis off"""
        if self.is_moving:
            raise RuntimeError("Can't set power off while axis is moving")

        self.__controller.set_off(self)
        state = self.__controller.state(self)
        self.settings.set("state", state)

    @property
    @lazy_init
    def _set_position(self):
        sp = self.settings.get("_set_position")
        if sp is not None:
            return sp
        if self._encoder_read_mode:
            # no setting, first time pos is read, init with controller hw pos.
            # issue 2463
            position = self._do_read_hw_position()
        else:
            position = self.position
        self._set_position = position
        return position

    @_set_position.setter
    @lazy_init
    def _set_position(self, new_set_pos):
        new_set_pos = float(
            new_set_pos
        )  # accepts both float or numpy array of 1 element
        self.settings.set("_set_position", new_set_pos)

    @property
    @lazy_init
    def measured_position(self):
        """
        Return measured position (ie: usually the encoder value).

        Returns:
            float: encoder value in user units
        """
        return self.dial2user(self.dial_measured_position)

    @property
    @lazy_init
    def dial_measured_position(self):
        """
        Dial encoder position.

        Returns:
            float: Dial encoder position
        """
        if self.encoder is not None:
            return self.encoder.read()
        else:
            raise RuntimeError("Axis '%s` has no encoder." % self.name)

    def __do_set_dial(self, new_dial):
        user_pos = self.position

        # Set the new dial on the encoder
        if self._encoder_read_mode:
            dial_pos = self.encoder.set(new_dial)
        else:
            # Send the new value in motor units to the controller
            # and read back the (atomically) reported position
            new_hw = new_dial * self.steps_per_unit
            hw_pos = self.__controller.set_position(self, new_hw)
            dial_pos = hw_pos / self.steps_per_unit
        self.settings.set("dial_position", dial_pos)

        if self.no_offset:
            self.__do_set_position(dial_pos, offset=0)
        else:
            # set user pos, will recalculate offset
            # according to new dial
            self.__do_set_position(user_pos)

        return dial_pos

    @property
    @lazy_init
    def dial(self):
        """
        Return current dial position, or set dial

        Returns:
            float: current dial position (dimensionless)
        """
        dial_pos = self.settings.get("dial_position")
        if dial_pos is None:
            dial_pos = self._update_dial()
        return dial_pos

    @dial.setter
    @lazy_init
    def dial(self, new_dial):
        if self.is_moving:
            raise RuntimeError(
                "%s: can't set axis dial position " "while moving" % self.name
            )
        new_dial = float(new_dial)  # accepts both float or numpy array of 1 element
        old_dial = self.dial
        new_dial = self.__do_set_dial(new_dial)
        print(f"'{self.name}` dial position reset from {old_dial} to {new_dial}")

    def __do_set_position(self, new_pos=None, offset=None):
        dial = self.dial
        curr_offset = self.offset
        if offset is None:
            # calc offset
            offset = new_pos - self.sign * dial
        if math.isnan(offset):
            # this can happen if dial is nan;
            # cannot continue
            return False
        if math.isclose(offset, 0):
            offset = 0
        if not math.isclose(curr_offset, offset):
            self.settings.set("offset", offset)
        if new_pos is None:
            # calc pos from offset
            new_pos = self.sign * dial + offset
        if math.isnan(new_pos):
            # do not allow to assign nan as a user position
            return False
        self.settings.set("position", new_pos)
        self._set_position = new_pos
        return True

    @property
    @lazy_init
    def position(self):
        """
        Return current user position, or set new user position in user units.

        Returns
        -------
            float: current user position (user units)

        Parameters
        ----------
        new_pos : float
            New position to set, in user units.

        Note
        ----
        This update offset.

        """
        pos = self.settings.get("position")
        if pos is None:
            pos = self.dial2user(self.dial)
            self.settings.set("position", pos)
        return pos

    @position.setter
    @lazy_init
    def position(self, new_pos):
        """See property getter"""
        log_debug(self, "axis.py : position(new_pos=%r)" % new_pos)
        if self.is_moving:
            raise RuntimeError(
                "%s: can't set axis user position " "while moving" % self.name
            )
        new_pos = float(new_pos)  # accepts both float or numpy array of 1 element
        curr_pos = self.position
        if self.no_offset:
            self.dial = new_pos
        if self.__do_set_position(new_pos):
            print(
                f"'{self.name}` position reset from {curr_pos} to {new_pos} (sign: {self.sign}, offset: {self.offset})"
            )

    @property
    def display_digits(self):
        """
        Return number of digits to use in position display.
        This value is determined according to the following rules:
        * use `display_digits` if defined in config.
        * use same number of digits than:
            `axis.steps_per_unit` if steps_per_unit != 1
            `axis.tolerance` otherwise

        NB: `axis.tolerance` should always exist.

        EX:
        """
        # Cached value.
        if self._display_digits is not None:
            return self._display_digits

        # Use `display_digits` value in config in priority.
        self._display_digits = self.config.get("display_digits")

        # `display_digits` not found in config => calculate a default value.
        if self._display_digits is None:
            if self.steps_per_unit < 2:  # Include usual case `steps_per_unit`==1.
                # Use tolerance.
                tol = self.tolerance
                #                print(f"{self.name} USE TOL")
                if tol >= 1:
                    self._display_digits = 2
                else:
                    # Count number of leading zeros in decimal part and add 1.
                    # * tolerance =  0.01   -> digits = 2
                    # * tolerance =  0.0001 -> digits = 4
                    # * tolerance = 12      -> digits = 2
                    decimal_part = str(tol).split(".")[1]
                    # print(f"decimal_part ={decimal_part}")
                    decimal_part_zlen = re.search("(?!0)", decimal_part).start()
                    self._display_digits = decimal_part_zlen + 1
            else:
                # Use steps_per_unit
                #                print(f"{self.name} USE SPU")
                # * steps_per_unit = 555 -> 1 step = 0.0018 -> digits = 4
                # * steps_per_unit =   0.1  -> digits = 0
                if self.steps_per_unit <= 1:
                    self._display_digits = 0
                self._display_digits = len(str(int(self.steps_per_unit))) + 1

        # Ensure value is an integer.
        if not isinstance(self._display_digits, int):
            log_error(
                self,
                f"in display_digits calculation for axis {self.name}: {self._display_digits} (use default: 5)",
            )
            self._display_digits = 5

        #       print( self.name, " steps_per_unit=", self.steps_per_unit,
        #            " tolerance=", self.tolerance, " dd=", self._display_digits, )

        return self._display_digits

    @lazy_init
    def _update_dial(self, update_user=True):
        dial_pos = self._hw_position
        update_list = (
            "dial_position",
            dial_pos,
        )
        if update_user:
            update_list += (
                "position",
                self.dial2user(dial_pos, self.offset),
            )
        self.settings.set(*update_list)
        return dial_pos

    @property
    @lazy_init
    def _hw_position(self):
        if self._encoder_read_mode:
            return self.dial_measured_position
        return self._do_read_hw_position()

    @lazy_init
    def _do_read_hw_position(self):
        try:
            curr_pos = self.__controller.read_position(self) / self.steps_per_unit
        except NotImplementedError:
            # this controller does not have a 'position'
            # (e.g like some piezo controllers)
            curr_pos = 0
        return curr_pos

    @property
    @lazy_init
    def state(self):
        """
        Return the axis state

        Return:
            AxisState: axis state
        """
        if self.is_moving:
            return AxisState("MOVING")
        state = self.settings.get("state")
        if state is None:
            # really read from hw
            state = self.hw_state
            self.settings.set("state", state)
        return state

    @property
    @lazy_init
    def hw_state(self):
        """Return the current hardware axis state (:obj:`AxisState`)"""
        return self.__controller.state(self)

    @lazy_init
    def __info__(self):
        """Standard method called by BLISS Shell info helper:
        Return common axis information about the axis.
        PLUS controller specific information.
        """
        from bliss.common.standard import info

        info_string = "AXIS:\n"

        try:
            # Config parameters.
            info_string += f"     name (R): {self.name}\n"
            info_string += f"     unit (R): {self.unit}\n"
            info_string += f"     offset (R): {self.offset:.5f}\n"
            info_string += f"     backlash (R): {self.backlash:.5f}\n"
            info_string += f"     sign (R): {self.sign}\n"
            info_string += f"     steps_per_unit (R): {self.steps_per_unit:.2f}\n"
            info_string += (
                f"     tolerance (R) (to check pos. before a move): {self.tolerance}\n"
            )

            if self.motion_hooks:
                info_string += "     motion_hooks (R):\n"
                for hook in self.motion_hooks:
                    info_string += f"          {hook}\n"
            else:
                info_string += "     motion_hooks (R): []\n"

            _low_cfg_limit, _high_cfg_limit = self.config_limits
            _lim = f"Low: {self.low_limit:.5f} High: {self.high_limit:.5f}"
            _cfg_lim = f"(config Low: {_low_cfg_limit:.5f} High: {_high_cfg_limit:.5f})"
            info_string += f"     limits (RW):    {_lim}    {_cfg_lim}\n"
            _dial = self.axis_rounder(self.dial)
            info_string += f"     dial (RW): {_dial}\n"
            _pos = self.axis_rounder(self.position)
            info_string += f"     position (RW): {_pos}\n"
        except Exception:
            info_string += "ERROR: unable to get info\n"

        try:
            info_string += f"     state (R): {self.state}\n"
        except Exception:
            info_string += "     ERROR: unable to get state\n"

        # ACCELERATION
        try:
            _acc = self.acceleration
            _acc_time = self.acctime

            if self.controller.axis_settings.config_setting["acceleration"]:
                _acc_config = f"{self.config_acceleration:10.5f}"
                _acc_time_config = f"{self.config_acctime:10.5f}"
            else:
                _acc_config = "none"
                _acc_time_config = "none"

            info_string += (
                f"     acceleration (RW): {_acc:10.5f}  (config: {_acc_config})\n"
            )
            info_string += f"     acctime (RW):      {_acc_time:10.5f}  (config: {_acc_time_config})\n"
        except Exception:
            info_string += "     acceleration: None\n"

        # VELOCITY
        try:
            _vel = self.velocity

            if self.controller.axis_settings.config_setting["velocity"]:
                _vel_config = f"{self.config_velocity:10.5f}"
            else:
                _vel_config = "none"

            info_string += (
                f"     velocity (RW):     {_vel:10.5f}  (config: {_vel_config})\n"
            )
            # velocity limits
            vel_low, vel_high = self.velocity_limits
            vel_config_low, vel_config_high = self.config_velocity_limits
            if vel_low is not None:
                info_string += f"     velocity_low_limit (RW):     {vel_low:10.5f}  (config: {vel_config_low})\n"
            if vel_high is not None:
                info_string += f"     velocity_high_limit (RW):     {vel_high:10.5f}  (config: {vel_config_high})\n"
        except Exception:
            info_string += "     velocity: None\n"

        # CONTROLLER
        try:
            info_string += info(self.__controller) + "\n"
        except Exception:
            info_string += "ERROR: Unable to get info from controller\n"

        # SPECIFIC AXIS INFO
        try:
            # usage of get_axis_info() to pass axis as param.
            info_string += self.__controller.get_axis_info(self) + "\n"
        except Exception:
            info_string += "ERROR: Unable to get axis info from controller\n"

        # ENCODER
        if self.encoder is not None:
            try:
                # Encoder is initialised here if not already done.
                info_string += info(self.encoder) + "\n"
            except Exception:
                info_string += "ERROR: Unable to get encoder info\n"
        else:
            info_string += "ENCODER:\n     None\n\n"

        # CLOSED_LOOP
        if self.closed_loop is not None:
            try:
                info_string += info(self.closed_loop)
            except Exception:
                info_string += "ERROR: Unable to get closed loop info\n"
        else:
            info_string += "CLOSED LOOP:\n     None\n"

        return info_string

    def sync_hard(self):
        """Forces an axis synchronization with the hardware"""
        self.settings.set("state", self.hw_state)
        self._update_dial()
        self._set_position = self.position
        if self.closed_loop is not None:
            self.closed_loop.sync_hard()
        event.send(self, "sync_hard")

    def _check_velocity_limits(self, new_velocity):
        min_velocity, max_velocity = self.velocity_limits
        if abs(new_velocity) > abs(max_velocity):
            raise ValueError(
                f"Velocity ({new_velocity}) exceeds max. velocity: {max_velocity}"
            )
        if min_velocity != float("inf") and abs(new_velocity) < abs(min_velocity):
            raise ValueError(
                f"Velocity ({new_velocity}) is below min. velocity: {min_velocity}"
            )

    @property
    @lazy_init
    def velocity(self):
        """
        Return or set the current velocity.

        Parameters:
            float: new_velocity in user unit/second
        Return:
            float: current velocity in user unit/second
        """
        # Read -> Return velocity read from motor axis.
        _user_vel = self.settings.get("velocity")
        if _user_vel is None:
            _user_vel = self.__controller.read_velocity(self) / abs(self.steps_per_unit)

        return _user_vel

    @velocity.setter
    @lazy_init
    def velocity(self, new_velocity):
        # Write -> Converts into motor units to change velocity of axis.
        new_velocity = float(
            new_velocity
        )  # accepts both float or numpy array of 1 element
        self._check_velocity_limits(new_velocity)

        if new_velocity < 0:
            raise RuntimeError(
                "Invalid velocity, the velocity cannot be a negative value"
            )

        try:
            self.__controller.set_velocity(
                self, new_velocity * abs(self.steps_per_unit)
            )
        except Exception as err:
            raise ValueError(
                "Cannot set value {} for {}".format(new_velocity, self.name)
            ) from err

        _user_vel = self.__controller.read_velocity(self) / abs(self.steps_per_unit)

        if not math.isclose(new_velocity, _user_vel, abs_tol=1e-4):
            log_warning(
                self,
                f"Controller velocity ({_user_vel}) is different from set velocity ({new_velocity})",
            )

        curr_vel = self.settings.get("velocity")
        if curr_vel != _user_vel:
            print(f"'{self.name}` velocity changed from {curr_vel} to {_user_vel}")
        self.settings.set("velocity", _user_vel)

        return _user_vel

    @property
    @lazy_init
    def config_velocity(self):
        """
        Return the config velocity.

        Return:
            float: config velocity (user units/second)
        """
        return self.__config_velocity

    @property
    @lazy_init
    def config_velocity_limits(self):
        """
        Return the config velocity limits.

        Return:
            (low_limit, high_limit): config velocity (user units/second)
        """
        return self.__config_velocity_low_limit, self.__config_velocity_high_limit

    @property
    def velocity_limits(self):
        return self.velocity_low_limit, self.velocity_high_limit

    @velocity_limits.setter
    def velocity_limits(self, limits):
        try:
            if len(limits) != 2:
                raise TypeError
        except TypeError:
            raise ValueError("Usage: .velocity_limits = low, high")
        ll = float_or_inf(limits[0], inf_sign=1)
        hl = float_or_inf(limits[1], inf_sign=1)
        self.settings.set("velocity_low_limit", ll)
        self.settings.set("velocity_high_limit", hl)

    @property
    @lazy_init
    def velocity_high_limit(self):
        """
        Return the limit max of velocity
        """
        return float_or_inf(self.settings.get("velocity_high_limit"))

    @velocity_high_limit.setter
    @lazy_init
    def velocity_high_limit(self, value):
        self.settings.set("velocity_high_limit", float_or_inf(value))

    @property
    @lazy_init
    def velocity_low_limit(self):
        """
        Return the limit max of velocity
        """
        return float_or_inf(self.settings.get("velocity_low_limit"))

    @velocity_low_limit.setter
    @lazy_init
    def velocity_low_limit(self, value):
        self.settings.set("velocity_low_limit", float_or_inf(value))

    def _set_jog_motion(self, motion, velocity):
        """Set jog velocity to controller

        Velocity is a signed value ; takes direction into account
        """
        velocity_in_steps = velocity * self.sign * self.steps_per_unit
        direction = 1 if velocity_in_steps > 0 else -1
        # assignment to motion object... this is abusing "target_pos" with velocity
        # and "delta" with direction
        motion.target_pos = abs(velocity_in_steps)
        motion.delta = direction

        backlash = self.backlash / self.sign * self.steps_per_unit
        if backlash:
            if math.copysign(direction, backlash) != direction:
                motion.backlash = backlash
        else:
            # don't do backlash correction
            motion.backlash = 0

    def _get_jog_motion(self):
        """Return motion object if axis is moving in jog mode

        Return values:
        - motion object, if axis is moving in jog mode
        - False if the jog move has been initiated by another BLISS
        - None if axis is not moving, or if there is no jog motion
        """
        if self.is_moving:
            if self._group_move.is_moving:
                for motions in self._group_move._motions_dict.values():
                    for motion in motions:
                        if motion.axis is self and motion.type == "jog":
                            return motion
            else:
                return False

    def _set_jog_velocity(self, new_velocity):
        """Set jog velocity

        If motor is moving, and we are in a jog move, the jog command is re-issued to
        set the new velocity.
        It is expected an error to be raised in case the controller does not support it.
        If the motor is not moving, only the setting is changed.

        Return values:
        - True if new velocity has been set
        - False if the jog move has been initiated by another BLISS ('external move')
        """
        motion = self._get_jog_motion()

        if motion is not None:
            if new_velocity == 0:
                self.stop()
            else:
                if motion:
                    self._set_jog_motion(motion, new_velocity)
                    self.controller.start_jog(self, motion.target_pos, motion.delta)
                else:
                    # jog move has been started externally
                    return False

        if new_velocity:
            # it is None the first time the channel is initialized,
            # it can be 0 to stop the jog move in this case we don't update the setting
            self.settings.set("jog_velocity", new_velocity)

        return True

    @property
    @lazy_init
    def jog_velocity(self):
        """
        Return the current jog velocity.

        Return:
            float: current jog velocity (user units/second)
        """
        # Read -> Return velocity read from motor axis.
        _user_jog_vel = self.settings.get("jog_velocity")
        if _user_jog_vel is None:
            _user_jog_vel = self.velocity
        return _user_jog_vel

    @jog_velocity.setter
    @lazy_init
    def jog_velocity(self, new_velocity):
        new_velocity = float(
            new_velocity
        )  # accepts both float or numpy array of 1 element
        if not self._set_jog_velocity(new_velocity):
            # move started externally => use channel to inform
            self._jog_velocity_channel.value = new_velocity

    @property
    @lazy_init
    def config_jog_velocity(self) -> float:
        """
        Returns the config jog velocity (user_units/second).
        """
        return self.__config_jog_velocity

    @property
    @lazy_init
    def acceleration(self) -> float:
        """
        Returns the acceleration.
        """
        _acceleration = self.settings.get("acceleration")
        if _acceleration is None:
            _ctrl_acc = self.__controller.read_acceleration(self)
            _acceleration = _ctrl_acc / abs(self.steps_per_unit)

        return _acceleration

    @acceleration.setter
    @lazy_init
    def acceleration(self, new_acc: float):
        """
        Parameters:
            new_acc: new acceleration that has to be provided in user_units/s2.

        Return:
            acceleration: acceleration (user_units/s2)
        """
        if self.is_moving:
            raise RuntimeError(
                "Cannot set acceleration while axis '%s` is moving." % self.name
            )
        new_acc = float(new_acc)  # accepts both float or numpy array of 1 element
        # Converts into motor units to change acceleration of axis.
        self.__controller.set_acceleration(self, new_acc * abs(self.steps_per_unit))
        _ctrl_acc = self.__controller.read_acceleration(self)
        _acceleration = _ctrl_acc / abs(self.steps_per_unit)
        curr_acc = self.settings.get("acceleration")
        if curr_acc != _acceleration:
            print(
                f"'{self.name}` acceleration changed from {curr_acc} to {_acceleration}"
            )
        self.settings.set("acceleration", _acceleration)
        return _acceleration

    @property
    @lazy_init
    def config_acceleration(self):
        """
        Acceleration specified in IN-MEMORY config.

        Note
        ----
        this is not necessarily the current acceleration.
        """
        return self.__config_acceleration

    @property
    @lazy_init
    def acctime(self):
        """
        Return the current acceleration time.

        Return:
            float: current acceleration time (second)
        """
        return abs(self.velocity / self.acceleration)

    @acctime.setter
    @lazy_init
    def acctime(self, new_acctime):
        # Converts acctime into acceleration.
        new_acctime = float(
            new_acctime
        )  # accepts both float or numpy array of 1 element
        self.acceleration = self.velocity / new_acctime
        return abs(self.velocity / self.acceleration)

    @property
    def config_acctime(self):
        """
        Return the config acceleration time.
        """
        return abs(self.config_velocity / self.config_acceleration)

    @property
    @lazy_init
    def jog_acctime(self):
        """
        Return the current acceleration time for jog move.

        Return:
            float: current acceleration time for jog move (second)
        """
        return abs(self.jog_velocity / self.acceleration)

    @property
    def config_jog_acctime(self):
        """
        Return the config acceleration time.
        """
        return abs(self.config_jog_velocity) / self.config_acceleration

    @property
    def dial_limits(self):
        ll = float_or_inf(self.settings.get("low_limit"), inf_sign=-1)
        hl = float_or_inf(self.settings.get("high_limit"), inf_sign=1)
        return ll, hl

    @dial_limits.setter
    @lazy_init
    def dial_limits(self, limits):
        """
        Set low, high limits in dial units
        """
        try:
            if len(limits) != 2:
                raise TypeError
        except TypeError:
            raise ValueError("Usage: .dial_limits = low, high")
        ll = float_or_inf(limits[0], inf_sign=-1)
        hl = float_or_inf(limits[1], inf_sign=1)
        self.settings.set("low_limit", ll)
        self.settings.set("high_limit", hl)

    @property
    @lazy_init
    def limits(self):
        """
        Return or set the current software limits in USER units.

        Return:
            tuple<float, float>: axis software limits (user units)

        Example:

            $ my_axis.limits = (-10,10)

        """
        return tuple(map(self.dial2user, self.dial_limits))

    @limits.setter
    @lazy_init
    def limits(self, limits):
        # Set limits (low, high) in user units.
        try:
            if len(limits) != 2:
                raise TypeError
        except TypeError:
            raise ValueError("Usage: .limits = low, high")

        # accepts iterable (incl. numpy array)
        self.low_limit, self.high_limit = (
            float(x) if x is not None else None for x in limits
        )

    @property
    @lazy_init
    def low_limit(self):
        # Return Low Limit in USER units.
        ll, hl = self.dial_limits
        return self.dial2user(ll)

    @low_limit.setter
    @lazy_init
    def low_limit(self, limit):
        # Sets Low Limit
        # <limit> must be given in USER units
        # Saved in settings in DIAL units
        if limit is not None:
            limit = float(limit)  # accepts numpy array of 1 element, or float
            limit = self.user2dial(limit)
        self.settings.set("low_limit", limit)

    @property
    @lazy_init
    def high_limit(self):
        # Return High Limit in USER units.
        ll, hl = self.dial_limits
        return self.dial2user(hl)

    @high_limit.setter
    @lazy_init
    def high_limit(self, limit):
        # Sets High Limit (given in USER units)
        # Saved in settings in DIAL units.
        if limit is not None:
            limit = float(limit)  # accepts numpy array of 1 element, or float
            limit = self.user2dial(limit)
        self.settings.set("high_limit", limit)

    @property
    @lazy_init
    def config_limits(self):
        """
        Return a tuple (low_limit, high_limit) from IN-MEMORY config in
        USER units.
        """
        ll_dial = self.__config_low_limit
        hl_dial = self.__config_high_limit
        return tuple(map(self.dial2user, (ll_dial, hl_dial)))

    def _update_settings(self, state=None):
        """Update position and state in redis

        By defaul, state is read from hardware; otherwise the given state is used
        Position is always read.

        In case of an exception (represented as X) during one of the readings,
        state is set to FAULT:

        state | pos | axis state | axis pos
        ------|-----|-----------------------
          OK  | OK  |   state    |  pos
          X   | OK  |   FAULT    |  pos
          OK  |  X  |   FAULT    |  not updated
          X   |  X  |   FAULT    |  not updated
        """
        state_reading_exc = None

        if state is None:
            try:
                state = self.hw_state
            except BaseException as exc:
                # save exception to re-raise it afterwards
                state_reading_exc = exc
                state = AxisState("FAULT")
        try:
            self._update_dial()
        except BaseException:
            state = AxisState("FAULT")
            raise
        finally:
            self.settings.set("state", state)
            if state_reading_exc:
                raise state_reading_exc

    def dial2user(self, position, offset=None):
        """
        Translates given position from DIAL units to USER units

        Args:
            position (float): position in dial units

        Keyword Args:
            offset (float): alternative offset. None (default) means use current offset

        Return:
            float: position in axis user units
        """
        if position is None:
            # see limits
            return None
        if offset is None:
            offset = self.offset
        return (self.sign * position) + offset

    def user2dial(self, position):
        """
        Translates given position from user units to dial units

        Args:
            position (float): position in user units

        Return:
            float: position in axis dial units
        """
        return (position - self.offset) / self.sign

    def _get_encoder_delta_steps(self, encoder_dial_pos):
        """
        Return the difference between given encoder position and motor controller indexer, in steps
        """
        if self._encoder_read_mode:
            controller_steps = self.__controller.read_position(self)
            enc_steps = encoder_dial_pos * self.steps_per_unit
            return controller_steps - enc_steps
        return 0

    def _get_motion(self, user_target_pos, polling_time=None) -> Motion | None:
        dial_target_pos = self.user2dial(user_target_pos)
        dial = self.dial
        target_pos = dial_target_pos * self.steps_per_unit
        delta = target_pos - dial * self.steps_per_unit
        encoder_delta_steps = self._get_encoder_delta_steps(dial)
        target_pos += encoder_delta_steps
        delta += encoder_delta_steps

        if self.controller._is_already_on_position(self, delta):
            return None  # Already in position => no motion

        motion = Motion(
            self,
            target_pos,
            delta,
        )

        backlash_str = ""
        backlash = self.backlash / self.sign * self.steps_per_unit
        if backlash:
            if abs(delta) > 0 and math.copysign(delta, backlash) != delta:
                # move and backlash are not in the same direction;
                # apply backlash correction, the move will happen
                # in 2 steps
                backlash_str = " (with %f backlash)"
                motion.backlash = backlash

        if polling_time is not None:
            motion.polling_time = polling_time

        low_limit_msg = "%s: move to `%s'%s would exceed low limit (%s)"
        high_limit_msg = "%s: move to `%s'%s would exceed high limit (%s)"
        user_low_limit, user_high_limit = self.limits
        low_limit = self.user2dial(user_low_limit) * self.steps_per_unit
        high_limit = self.user2dial(user_high_limit) * self.steps_per_unit

        # check software limits
        if high_limit < low_limit:
            high_limit, low_limit = low_limit, high_limit
            user_high_limit, user_low_limit = user_low_limit, user_high_limit
            high_limit_msg, low_limit_msg = low_limit_msg, high_limit_msg

        if motion.target_pos < low_limit:
            raise ValueError(
                low_limit_msg
                % (self.name, user_target_pos, backlash_str, user_low_limit)
            )
        if motion.target_pos > high_limit:
            raise ValueError(
                high_limit_msg
                % (self.name, user_target_pos, backlash_str, user_high_limit)
            )

        return motion

    @lazy_init
    def get_motion(
        self, user_target_pos, relative=False, polling_time=None
    ) -> Motion | None:
        """Prepare a motion. Internal usage only"""

        # To accept both float or numpy array of 1 element
        user_target_pos = float(user_target_pos)

        log_debug(
            self,
            "get_motion: user_target_pos=%g, relative=%r" % (user_target_pos, relative),
        )

        if relative:
            # start from last set position
            user_initial_pos = self._set_position
            user_target_pos += user_initial_pos

        motion = self._get_motion(user_target_pos, polling_time)
        # We are already in position
        # Don't need to go further.
        if motion is None:
            self._set_position = user_target_pos
            return None

        dial_initial_pos = self.dial
        hw_pos = self._hw_position
        check_discrepancy = self.config.get("check_discrepancy", bool, True) and (
            not (self._encoder_read_mode and not self._check_encoder)
        )

        diff_discrepancy = abs(dial_initial_pos - hw_pos)
        if check_discrepancy and diff_discrepancy > self.tolerance:
            raise RuntimeError(
                "%s: discrepancy between dial (%f) and controller position (%f)\n \
                     diff=%g tolerance=%g => aborting movement."
                % (
                    self.name,
                    dial_initial_pos,
                    hw_pos,
                    diff_discrepancy,
                    self.tolerance,
                )
            )

        return motion

    def _set_moving_state(self, from_channel=False):
        self.__move_done.clear()
        self.__move_done_callback.clear()
        _emit_move_done(self, value=False, from_channel=from_channel)

        moving_state = AxisState("MOVING")
        if from_channel:
            event.send_safe(self, "state", moving_state)
        else:
            self.settings.set("state", moving_state)

    def _set_move_done(self, from_channel=False):
        with contextlib.ExitStack() as move_done:
            move_done.callback(self.__move_done_callback.set)
            move_done.callback(_emit_move_done, self, from_channel=from_channel)
            move_done.callback(self.__move_done.set)
            if not from_channel:
                move_done.callback(self._update_settings)

    def _check_ready(self):
        if not self.controller.check_ready_to_move(self, self.state):
            raise RuntimeError("axis %s state is " "%r" % (self.name, str(self.state)))

    @lazy_init
    def move(self, user_target_pos, wait=True, relative=False, polling_time=None):
        """
        Move axis to the given absolute/relative position

        Parameters:
            user_target_pos: float
                Destination (user units)
            wait : bool, optional
                Wait or not for end of motion
            relative : bool
                False if *user_target_pos* is given in absolute position or True if it is given in relative position
            polling_time : float
                Motion loop polling time (seconds)

        Raises:
            RuntimeError

        Returns:
            None

        """
        # accepts both floats and numpy arrays of 1 element
        user_target_pos = float(user_target_pos)

        if not numpy.isfinite(user_target_pos):
            raise ValueError(
                f"axis {self.name} cannot be moved to position: {user_target_pos}"
            )

        log_debug(
            self,
            "user_target_pos=%g  wait=%r relative=%r"
            % (user_target_pos, wait, relative),
        )
        with self._lock:
            if self.is_moving:
                raise RuntimeError("axis %s state is %r" % (self.name, "MOVING"))

            self._group_move = GroupMove()
            self._group_move.move(
                {self: user_target_pos},
                _prepare_one_controller_motions,
                _start_one_controller_motions,
                _stop_one_controller_motions,
                wait=False,
                relative=relative,
                polling_time=polling_time,
            )

        if wait:
            self.wait_move()

    def _handle_move(self, motion, ctrl_state_func="state", limit_error=True):
        state = None
        try:
            state = self._move_loop(motion.polling_time, ctrl_state_func, limit_error)
        finally:
            motion.last_state = state
        return state

    def _do_encoder_reading(self):
        enc_dial = self.encoder.read()
        curr_pos = self._update_dial()
        if abs(curr_pos - enc_dial) > self.encoder.tolerance:
            raise RuntimeError(
                f"'{self.name}' didn't reach final position."
                f"(enc_dial={enc_dial:10.5f}, curr_pos={curr_pos:10.5f} "
                f"diff={enc_dial-curr_pos:10.5f} enc.tol={self.encoder.tolerance:10.5f})"
            )

    @lazy_init
    def jog(self, velocity=None, reset_position=None, polling_time=None):
        """
        Start to move axis at constant velocity

        Args:
            velocity: signed velocity for constant speed motion
        """
        if velocity is not None:
            velocity = float(
                velocity
            )  # accepts both floats or numpy arrays of 1 element

            if self._get_jog_motion() is not None:
                # already in jog move
                self.jog_velocity = velocity
                return
        else:
            velocity = self.jog_velocity

        self._check_velocity_limits(velocity)

        with self._lock:
            if self.is_moving:
                raise RuntimeError("axis %s state is %r" % (self.name, "MOVING"))

            if velocity == 0:
                return

            self.jog_velocity = velocity

            motion = Motion(self, None, None, "jog")
            motion.polling_time = polling_time
            motion.saved_velocity = self.velocity
            motion.reset_position = reset_position
            self._set_jog_motion(
                motion, velocity
            )  # this will complete motion configuration

            def start_jog(controller, motions):
                controller.start_jog(motions[0].axis, motion.target_pos, motion.delta)

            def stop_one(controller, motions):
                controller.stop_jog(motions[0].axis)

            self._group_move = GroupMove()
            self._group_move.start(
                {self.controller: [motion]},
                None,  # no prepare
                start_jog,
                stop_one,
                "_jog_move",
                wait=False,
            )

    def _jog_move(self, motion):
        # for the record: for jog move, motion object .target_pos and .delta have a different meaning:
        # velocity = motion.target_pos
        # direction = motion.delta
        return self._handle_move(motion)

    def _jog_cleanup(self, saved_velocity, reset_position):
        self.velocity = saved_velocity

        if reset_position is None:
            self.settings.clear("_set_position")
        elif reset_position == 0:
            self.__do_set_dial(0)
        elif callable(reset_position):
            reset_position(self)

    def rmove(self, user_delta_pos, wait=True, polling_time=None):
        """
        Move axis to the given relative position.

        Same as :meth:`move` *(relative=True)*

        Args:
            user_delta_pos: motor displacement (user units)
        Keyword Args:
            wait (bool): wait or not for end of motion
            polling_time (float): motion loop polling time (seconds)
        """
        log_debug(self, "user_delta_pos=%g  wait=%r" % (user_delta_pos, wait))
        return self.move(user_delta_pos, wait, relative=True, polling_time=polling_time)

    def wait_move(self):
        """
        Wait for the axis to finish motion (blocks current :class:`Greenlet`)
        """
        try:
            self.__move_done_callback.wait()
        except BaseException:
            self.stop()
            raise
        finally:
            if self._group_move._move_task is not None:
                self._group_move._move_task.get()

    def _move_loop(self, polling_time, ctrl_state_func, limit_error=True):
        state_funct = getattr(self.__controller, ctrl_state_func)
        while True:
            state = state_funct(self)
            self._update_settings(state)
            if not state.MOVING:
                if limit_error and (state.LIMPOS or state.LIMNEG):
                    raise AxisOnLimitError(
                        f"{self.name}: {str(state)} at {self.position}"
                    )
                elif state.OFF:
                    raise AxisOffError(f"{self.name}: {str(state)}")
                elif state.FAULT:
                    raise AxisFaultError(f"{self.name}: {str(state)}")
                return state
            gevent.sleep(polling_time)

    @lazy_init
    def stop(self, wait=True):
        """
        Stops the current motion

        If axis is not moving returns immediately

        Args:
            wait (bool): wait for the axis to decelerate before returning \
            [default: True]
        """
        if self.is_moving:
            if self._group_move._move_task:
                self._group_move.stop(wait)
            else:
                # move started externally
                self._move_stop_channel.value = True

            if wait:
                self.wait_move()

    def _external_stop(self, stop):
        if stop:
            self.stop()

    @lazy_init
    def home(self, switch=1, wait=True, polling_time=None):
        """
        Searches the home switch

        Args:
            wait (bool): wait for search to finish [default: True]
        """
        with self._lock:
            if self.is_moving:
                raise RuntimeError("axis %s state is %r" % (self.name, "MOVING"))

            # create motion object for hooks
            motion = Motion(
                self,
                switch,
                None,
                "homing",
                "home",
            )
            motion.polling_time = (
                self._polling_time if polling_time is None else polling_time
            )

            def start_one(controller, motions):
                controller.home_search(motions[0].axis, motions[0].target_pos)

            def stop_one(controller, motions):
                controller.stop(motions[0].axis)

            self._group_move = GroupMove()
            self._group_move.start(
                {self.controller: [motion]},
                None,  # no prepare
                start_one,
                stop_one,
                "_wait_home",
                wait=False,
            )
        if wait:
            self.wait_move()

    def _wait_home(self, motion):
        return self._handle_move(motion, ctrl_state_func="home_state")

    @lazy_init
    def hw_limit(self, limit, wait=True, polling_time=None):
        """
        Go to a hardware limit

        Args:
            limit (int): positive means "positive limit"
            wait (bool): wait for axis to finish motion before returning \
            [default: True]
        """
        limit = int(limit)
        with self._lock:
            if self.is_moving:
                raise RuntimeError("axis %s state is %r" % (self.name, "MOVING"))

            motion = Motion(
                self,
                limit,
                None,
                "limit_search",
                "lim+" if limit > 0 else "lim-",
            )
            motion.polling_time = (
                self._polling_time if polling_time is None else polling_time
            )

            def start_one(controller, motions):
                controller.limit_search(motions[0].axis, motions[0].target_pos)

            def stop_one(controller, motions):
                controller.stop(motions[0].axis)

            self._group_move = GroupMove()
            self._group_move.start(
                {self.controller: [motion]},
                None,  # no prepare
                start_one,
                stop_one,
                "_wait_limit_search",
                wait=False,
            )

        if wait:
            self.wait_move()

    def _wait_limit_search(self, motion):
        return self._handle_move(motion, limit_error=False)

    def settings_to_config(
        self, velocity=True, acceleration=True, limits=True, sign=True, backlash=True
    ):
        """
        Set settings values in in-memory config then save it in file.
        Settings to save can be specified.
        """
        if velocity:
            ll, hl = self.velocity_limits
            self.__config.set("velocity", self.velocity)
            self.__config.set("velocity_low_limit", ll)
            self.__config.set("velocity_high_limit", hl)
        if acceleration:
            self.__config.set("acceleration", self.acceleration)
        if limits:
            ll, hl = self.dial_limits
            self.__config.set("low_limit", ll)
            self.__config.set("high_limit", hl)
        if sign:
            self.__config.set("sign", self.sign)
        if backlash:
            self.__config.set("backlash", self.backlash)

        if any((velocity, acceleration, limits, sign, backlash)):
            self.__config.save()
            self._init_config_properties(
                velocity=velocity,
                acceleration=acceleration,
                limits=limits,
                sign=sign,
                backlash=backlash,
            )

    def apply_config(
        self,
        reload=False,
        velocity=True,
        acceleration=True,
        limits=True,
        sign=True,
        backlash=True,
    ):
        """
        Applies configuration values (yml) to the current settings.

        Note
        ----
        This resets the axis settings to those specified in the config

        Parameters
        ----------
        reload : bool
            if True config files are reloaded by beacon.
        """
        if reload:
            self.config.reload()

        if self._closed_loop is not None:
            self._closed_loop.apply_config(reload)

        if self.encoder is not None:
            self.encoder.apply_config(reload)

        self._init_config_properties(
            velocity=velocity,
            acceleration=acceleration,
            limits=limits,
            sign=sign,
            backlash=backlash,
        )

        if velocity:
            self.settings.clear("velocity")
            self.settings.clear("velocity_low_limit")
            self.settings.clear("velocity_high_limit")
        if acceleration:
            self.settings.clear("acceleration")
        if limits:
            self.settings.clear("low_limit")
            self.settings.clear("high_limit")
        if sign:
            self.settings.clear("sign")
        if backlash:
            self.settings.clear("backlash")

        self._disabled = False
        self.settings.init()

        # update position (needed for sign change)
        pos = self.dial2user(self.dial)
        if self.position != pos:
            try:
                self.position = self.dial2user(self.dial)
            except NotImplementedError:
                pass

    @lazy_init
    def set_event_positions(self, positions):
        dial_positions = self.user2dial(numpy.array(positions, dtype=float))
        step_positions = dial_positions * self.steps_per_unit
        return self.__controller.set_event_positions(self, step_positions)

    @lazy_init
    def get_event_positions(self):
        step_positions = numpy.array(
            self.__controller.get_event_positions(self), dtype=float
        )
        dial_positions = self.dial2user(step_positions)
        return dial_positions / self.steps_per_unit

    @lazy_init
    def dataset_metadata(self):
        return {"name": self.name, "value": self.position}


class AxisState:
    """
    Standard states:
      MOVING  : 'Axis is moving'
      READY   : 'Axis is ready to be moved (not moving ?)'
      FAULT   : 'Error from controller'
      LIMPOS  : 'Hardware high limit active'
      LIMNEG  : 'Hardware low limit active'
      HOME    : 'Home signal active'
      OFF     : 'Axis power is off'
      DISABLED: 'Axis cannot move (must be enabled - not ready ?)'

    When creating a new instance, you can pass any number of arguments, each
    being either a string or tuple of strings (state, description). They
    represent custom axis states.
    """

    #: state regular expression validator
    STATE_VALIDATOR = re.compile(r"^[A-Z0-9]+\s*$")

    _STANDARD_STATES = {
        "READY": "Axis is READY",
        "MOVING": "Axis is MOVING",
        "FAULT": "Error from controller",
        "LIMPOS": "Hardware high limit active",
        "LIMNEG": "Hardware low limit active",
        "HOME": "Home signal active",
        "OFF": "Axis power is off",
        "DISABLED": "Axis cannot move",
    }

    @property
    def READY(self):
        """Axis is ready to be moved"""
        return "READY" in self._current_states

    @property
    def MOVING(self):
        """Axis is moving"""
        return "MOVING" in self._current_states

    @property
    def FAULT(self):
        """Error from controller"""
        return "FAULT" in self._current_states

    @property
    def LIMPOS(self):
        """Hardware high limit active"""
        return "LIMPOS" in self._current_states

    @property
    def LIMNEG(self):
        """Hardware low limit active"""
        return "LIMNEG" in self._current_states

    @property
    def OFF(self):
        """Axis power is off"""
        return "OFF" in self._current_states

    @property
    def HOME(self):
        """Home signal active"""
        return "HOME" in self._current_states

    @property
    def DISABLED(self):
        """Axis is disabled (must be enabled to move (not ready ?))"""
        return "DISABLED" in self._current_states

    def __init__(self, *states):
        """
        <*states> : can be one or many string or tuple of strings (state, description)
        """

        # set of active states.
        self._current_states = list()

        # dict of descriptions of states.
        self._state_desc = self._STANDARD_STATES

        for state in states:
            if isinstance(state, tuple):
                self.create_state(*state)
                self.set(state[0])
            else:
                if isinstance(state, AxisState):
                    state = state.current_states()
                self._set_state_from_string(state)

    def states_list(self):
        """
        Return a list of available/created states for this axis.
        """
        return list(self._state_desc)

    def _check_state_name(self, state_name):
        if not isinstance(state_name, str) or not AxisState.STATE_VALIDATOR.match(
            state_name
        ):
            raise ValueError(
                "Invalid state: a state must be a string containing only block letters"
            )

    def _has_custom_states(self):
        return self._state_desc is not AxisState._STANDARD_STATES

    def create_state(self, state_name, state_desc=None):
        """
        Adds a new custom state

        Args:
            state_name (str): name of the new state
        Keyword Args:
            state_desc (str): state description [default: None]

        Raises:
            ValueError: if state_name is invalid
        """
        # Raises ValueError if state_name is invalid.
        self._check_state_name(state_name)
        if state_desc is not None and "|" in state_desc:
            raise ValueError(
                "Invalid state: description contains invalid character '|'"
            )

        # if it is the first time we are creating a new state, create a
        # private copy of standard states to be able to modify locally
        if not self._has_custom_states():
            self._state_desc = AxisState._STANDARD_STATES.copy()

        if state_name not in self._state_desc:
            # new description is put in dict.
            if state_desc is None:
                state_desc = "Axis is %s" % state_name
            self._state_desc[state_name] = state_desc

            # Makes state accessible via a class property.
            # NO: we can't, because the objects of this class will become unpickable,
            # as the class changes...
            # Error message is: "Can't pickle class XXX: it's not the same object as XXX"
            # add_property(self, state_name, lambda _: state_name in self._current_states)

    """
    Flags ON a given state.
    ??? what about other states : clear other states ???  -> MG : no
    ??? how to flag OFF ???-> no : on en cree un nouveau.
    """

    def set(self, state_name):
        """
        Activates the given state on this AxisState

        Args:
            state_name (str): name of the state to activate

        Raises:
            ValueError: if state_name is invalid
        """
        if state_name in self._state_desc:
            if state_name not in self._current_states:
                self._current_states.append(state_name)

                # Mutual exclusion of READY and MOVING
                if state_name == "READY":
                    if self.MOVING:
                        self._current_states.remove("MOVING")
                if state_name == "MOVING":
                    if self.READY:
                        self._current_states.remove("READY")
        else:
            raise ValueError("state %s does not exist" % state_name)

    def unset(self, state_name):
        """
        Deactivates the given state on this AxisState

        Args:
            state_name (str): name of the state to deactivate

        Raises:
            ValueError: if state_name is invalid
        """
        self._current_states.remove(state_name)

    def clear(self):
        """Clears all current states"""
        # Flags all states off.
        self._current_states = list()

    @property
    def current_states_names(self):
        """
        Return a list of the current states names
        """
        return self._current_states[:]

    def current_states(self):
        """
        Return a string of current states.

        Return:
            str: *|* separated string of current states or string *UNKNOWN* \
            if there is no current state
        """
        states = [
            "%s%s"
            % (
                state.rstrip(),
                " (%s)" % self._state_desc[state]
                if self._state_desc.get(state)
                else "",
            )
            for state in map(str, self._current_states)
        ]

        if len(states) == 0:
            return "UNKNOWN"

        return " | ".join(states)

    def _set_state_from_string(self, state):
        # is state_name a full list of states returned by self.current_states() ?
        # (copy constructor)
        if "(" in state:
            full_states = [s.strip() for s in state.split("|")]
            p = re.compile(r"^([A-Z0-9]+)\s\((.+)\)", re.DOTALL)
            for full_state in full_states:
                m = p.match(full_state)
                state = m.group(1)
                desc = m.group(2)
                self.create_state(state, desc)
                self.set(state)
        else:
            if state != "UNKNOWN":
                self.create_state(state)
                self.set(state)

    def __str__(self):
        return self.current_states()

    def __repr__(self):
        return "AxisState: %s" % self.__str__()

    def __contains__(self, other):
        if isinstance(other, str):
            if not self._current_states:
                return other == "UNKNOWN"
            return other in self._current_states
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, str):
            warnings.warn("Use: **%s in state** instead" % other, DeprecationWarning)
            return self.__contains__(other)
        elif isinstance(other, AxisState):
            return set(self._current_states) == set(other._current_states)
        else:
            return NotImplemented

    def new(self, share_states=True):
        """
        Create a new AxisState which contains the same possible states but no
        current state.

        If this AxisState contains custom states and *share_states* is True
        (default), the possible states are shared with the new AxisState.
        Otherwise, a copy of possible states is created for the new AxisState.

        Keyword Args:
            share_states: If this AxisState contains custom states and
                          *share_states* is True (default), the possible states
                          are shared with the new AxisState. Otherwise, a copy
                          of possible states is created for the new AxisState.

        Return:
            AxisState: a copy of this AxisState with no current states
        """
        result = AxisState()
        if self._has_custom_states() and not share_states:
            result._state_desc = self._state_desc.copy()
        else:
            result._state_desc = self._state_desc
        return result


class ModuloAxis(Axis):
    def __init__(self, *args, **kwargs):
        Axis.__init__(self, *args, **kwargs)

        self._modulo = self.config.get("modulo", float)
        self._in_prepare_move = False

    def __calc_modulo(self, pos):
        return pos % self._modulo

    @property
    def dial(self):
        d = super(ModuloAxis, self).dial
        if self._in_prepare_move:
            return d
        else:
            return self.__calc_modulo(d)

    @dial.setter
    def dial(self, value):
        super(ModuloAxis, self.__class__).dial.fset(self, value)
        return self.dial

    def get_motion(self, user_target_pos, *args, **kwargs):
        user_target_pos = self.__calc_modulo(user_target_pos)
        self._in_prepare_move = True
        try:
            return Axis.get_motion(self, user_target_pos, *args, **kwargs)
        finally:
            self._in_prepare_move = False


class NoSettingsAxis(Axis):
    def __init__(self, *args, **kwags):
        super().__init__(*args, **kwags)
        for setting_name in self.settings.setting_names:
            self.settings.disable_cache(setting_name)


class CalcAxis(Axis):
    @property
    def state(self):
        return self.controller.state(self)

    @property
    def hw_state(self):
        return self.controller.hw_state(self)

    def sync_hard(self):
        """Forces an axis synchronization with the hardware"""
        for pseudo in self.controller.pseudos:
            if pseudo.is_moving:
                raise RuntimeError(f"cannot sync {pseudo.name} while moving")

        self.controller.sync_hard()

    def update_position(self):
        deprecated_warning(
            kind="method",
            name="update_position",
            replacement="sync_hard",
            reason="for homogeneity reasons",
            since_version="1.11",
            skip_backtrace_count=5,
            only_once=False,
        )
        return self.sync_hard()
