# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import functools
import gevent
import gevent.lock
import os
import weakref
import time
import datetime
import collections
import warnings
from typing import Callable, Any, Dict
import logging
import numpy
from contextlib import contextmanager, ExitStack

from bliss.common.types import _countable
from bliss import current_session, is_bliss_shell
from bliss.common.axis import Axis, CalcAxis
from bliss.common.motor_group import is_motor_group, Group
from bliss.common.hook import group_hooks, execute_pre_scan_hooks
from bliss.common import event
from bliss.common.cleanup import error_cleanup, axis as cleanup_axis, capture_exceptions
from bliss.common.greenlet_utils import KillMask
from bliss.common import plot as plot_mdl
from bliss.common.utils import deep_update, rounder, typecheck
from bliss.scanning.scan_meta import (
    META_TIMING,
    ScanMeta,
    get_user_scan_meta,
    get_controllers_scan_meta,
)
from bliss.scanning.scan_state import ScanState
from bliss.controllers.motor import get_real_axes
from blissdata.client import get_redis_proxy
from blissdata.data.node import create_node, DataNodeAsyncHelper
from blissdata.data.nodes import channel as channelnode
from blissdata.data.nodes.channel import RedisDataExpiredError
from blissdata.data.nodes.scan import get_data_from_nodes
from blissdata.common.utils import get_matching_names
from bliss.scanning.chain import AcquisitionSlave, AcquisitionMaster, StopChain
from bliss.scanning.writer.null import Writer as NullWriter
from bliss.scanning import scan_math
from bliss.common.logtools import disable_user_output
from bliss.common.plot import get_plot
from bliss import __version__ as publisher_version
from bliss.scanning.scan_info import ScanInfo
from bliss.common.counter import Counter

from nexus_writer_service.utils import scan_utils
from blissdata.h5api import dynamic_hdf5

logger = logging.getLogger("bliss.scans")


_scan_progress_class = None


def get_default_scan_progress():
    if _scan_progress_class:
        return _scan_progress_class()


class ScanAbort(BaseException):
    pass


def is_zerod(node):
    return node.type == "channel" and len(node.shape) == 0


class WatchdogCallback:
    """
    This class is a watchdog for scan class.  It's role is to follow
    if detectors involved in the scan have the right behavior. If not
    the callback may raise an exception.
    All exception will bubble-up except StopIteration which will just stop
    the scan.
    """

    def __init__(self, watchdog_timeout=1.0):
        """
        watchdog_timeout -- is the maximum calling frequency of **on_timeout**
        method.
        """
        self.__watchdog_timeout = watchdog_timeout

    @property
    def timeout(self):
        return self.__watchdog_timeout

    def on_timeout(self):
        """
        This method is called when **watchdog_timeout** elapsed it means
        that no data event is received for the time specified by
        **watchdog_timeout**
        """
        pass

    def on_scan_new(self, scan, scan_info):
        """
        Called when scan is starting
        """
        pass

    def on_scan_data(self, data_events, nodes, scan_info):
        """
        Called when new data are emitted by the scan.  This method should
        raise en exception to stop the scan.  All exception will
        bubble-up exception the **StopIteration**.  This one will just
        stop the scan.
        """
        pass

    def on_scan_end(self, scan_info):
        """
        Called at the end of the scan
        """
        pass


class _WatchDogTask(gevent.Greenlet):
    def __init__(self, scan, callback):
        super().__init__()
        self._scan = weakref.proxy(scan, self.stop)
        self._events = gevent.queue.Queue()
        self._data_events = dict()
        self._callback = callback
        self.__watchdog_timer = None
        self._lock = gevent.lock.Semaphore()
        self._lock_watchdog_reset = gevent.lock.Semaphore()

    def trigger_data_event(self, sender, signal):
        self._reset_watchdog()
        event_set = self._data_events.setdefault(sender, set())
        event_set.add(signal)
        if not len(self._events):
            self._events.put("Data Event")

    def on_scan_new(self, scan, scan_info):
        self._callback.on_scan_new(scan, scan_info)
        self._reset_watchdog()

    def on_scan_end(self, scan_info):
        self.stop()
        self._callback.on_scan_end(scan_info)

    def stop(self):
        self.clear_queue()
        self._events.put(StopIteration)

    def kill(self):
        super().kill()
        if self.__watchdog_timer is not None:
            self.__watchdog_timer.kill()

    def clear_queue(self):
        while True:
            try:
                self._events.get_nowait()
            except gevent.queue.Empty:
                break

    def _run(self):
        try:
            for ev in self._events:
                if isinstance(ev, BaseException):
                    raise ev
                try:
                    if self._data_events:
                        data_event = self._data_events
                        self._data_events = dict()
                        # disable the watchdog before calling the callback
                        if self.__watchdog_timer is not None:
                            self.__watchdog_timer.kill()
                        with KillMask():
                            with self._lock:
                                self._callback.on_scan_data(
                                    data_event, self._scan.nodes, self._scan.scan_info
                                )
                        # reset watchdog if it wasn't restarted in between
                        if not self.__watchdog_timer:
                            self._reset_watchdog()

                except StopIteration:
                    break
        finally:
            if self.__watchdog_timer is not None:
                self.__watchdog_timer.kill()

    def _reset_watchdog(self):
        with self._lock_watchdog_reset:
            if self.__watchdog_timer:
                self.__watchdog_timer.kill()

            if self.ready():
                return

            def loop(timeout):
                while True:
                    gevent.sleep(timeout)
                    try:
                        with KillMask():
                            with self._lock:
                                self._callback.on_timeout()
                    except StopIteration:
                        self.stop()
                        break
                    except BaseException as e:
                        self.clear_queue()
                        self._events.put(e)
                        break

            self.__watchdog_timer = gevent.spawn(loop, self._callback.timeout)


class ScanPreset:
    def __init__(self):
        self.__acq_chain = None

    @property
    def acq_chain(self):
        return self.__acq_chain

    def _prepare(self, scan):
        """
        Called on the preparation phase of a scan.
        """
        self.__acq_chain = scan.acq_chain
        self.__new_channel_data = {}
        self.__new_data_callback = None
        return self.prepare(scan)

    def prepare(self, scan):
        """
        Called on the preparation phase of a scan.
        To be overwritten in user scan presets
        """
        pass

    def start(self, scan):
        """
        Called on the starting phase of a scan.
        """
        pass

    def _stop(self, scan):
        if self.__new_channel_data:
            for data_chan in self.__new_channel_data.keys():
                event.disconnect(data_chan, "new_data", self.__new_channel_data_cb)
        self.__new_data_callback = None
        self.__new_channel_data = {}
        return self.stop(scan)

    def stop(self, scan):
        """
        Called at the end of a scan.
        """
        pass

    def __new_channel_data_cb(self, event_dict, sender=None):
        data = event_dict.get("data")
        if data is None:
            return
        counter = self.__new_channel_data[sender]
        return self.__new_data_callback(counter, sender.fullname, data)

    def connect_data_channels(self, counters_list, callback):
        """
        Associate a callback to the data emission by the channels of a list of counters.

        Args:
            counters_list: the list of counters to connect data channels to
            callback: a callback function
        """
        nodes = self.acq_chain.get_node_from_devices(*counters_list)
        for i, node in enumerate(nodes):
            try:
                channels = node.channels
            except AttributeError:
                continue
            else:
                self.__new_data_callback = callback
                cnt = counters_list[i]
                for data_chan in channels:
                    self.__new_channel_data[data_chan] = cnt
                    event.connect(data_chan, "new_data", self.__new_channel_data_cb)


class _ScanIterationsRunner:
    """Helper class to execute iterations of a scan

    Uses a generator to execute the different steps, as it receives tasks via 'send'
    """

    def __init__(self):
        self.runner = self._run()  # make generator
        next(self.runner)  # "prime" runner: go to first yield

    def _gwait(self, greenlets, masked_kill_nb=0):
        """Wait until given greenlets are all done

        In case of error, greenlets are all killed and exception is raised

        If a kill happens (GreenletExit or KeyboardInterrupt exception)
        while waiting for greenlets, wait is retried - 'masked_kill_nb'
        allow to specify a number of 'kills' to mask to really kill only
        if it insists.
        """
        try:
            gevent.joinall(greenlets, raise_error=True)
        except (gevent.GreenletExit, KeyboardInterrupt):
            # in case of kill: give a chance to finish the task,
            # but if it insists => let it kill
            if masked_kill_nb > 0:
                with KillMask(masked_kill_nb=masked_kill_nb):
                    gevent.joinall(greenlets)
            raise
        finally:
            if any(
                greenlets
            ):  # only kill if some greenlets are still running, as killall takes time
                gevent.killall(greenlets)

    def _run_next(self, scan, next_iter):
        next_iter.start()
        for i in next_iter:
            i.prepare(scan, scan.scan_info)
            i.start()

    def send(self, arg):
        """Delegate 'arg' to generator"""
        try:
            return self.runner.send(arg)
        except StopIteration:
            pass

    def _run(self):
        """Generator that runs a scan: from applying parameters to acq. objects then preparing and up to stopping

        Goes through the different steps by receiving tasks from the caller Scan object
        """
        apply_parameters_tasks = yield

        # apply parameters in parallel on all iterators
        self._gwait(apply_parameters_tasks)

        # execute prepare tasks in parallel
        prepare_tasks = yield
        self._gwait(prepare_tasks)

        # scan tasks
        scan, chain_iterators, watchdog_task = yield
        tasks = {gevent.spawn(self._run_next, scan, i): i for i in chain_iterators}
        if watchdog_task is not None:
            # put watchdog task in list, but there is no corresponding iterator
            tasks[watchdog_task] = None

        with capture_exceptions(raise_index=0) as capture:
            with capture():
                try:
                    # gevent.iwait iteratively yield objects as they are ready
                    with gevent.iwait(tasks) as task_iter:
                        # loop over ready tasks until all are consumed, or an
                        # exception is raised
                        for t in task_iter:
                            t.get()  # get the task result ; this may raise an exception

                            if t is watchdog_task:
                                # watchdog task ended: stop the scan
                                raise StopChain
                            elif tasks[t].top_master.terminator:
                                # a task with a terminator top master has finished:
                                # scan has to end
                                raise StopChain
                except StopChain:
                    # stop scan:
                    # kill all tasks, but do not raise an exception
                    gevent.killall(tasks, exception=StopChain)
                except (gevent.GreenletExit, KeyboardInterrupt):
                    # scan gets killed:
                    # kill all tasks, re-raise exception
                    gevent.killall(tasks, exception=gevent.GreenletExit)
                    raise
                except BaseException:
                    # an error occured: kill all tasks, re-raise exception
                    gevent.killall(tasks, exception=StopChain)
                    raise

            stop_tasks = yield
            with capture():
                self._gwait(stop_tasks, masked_kill_nb=1)


class Scan:
    _NODE_TYPE = "scan"
    SCAN_NUMBER_LOCK = gevent.lock.Semaphore()

    # When enabled, only the scan/channel node's info and struct are
    # cached, not the channel data.
    _REDIS_CACHING = True

    def __init__(
        self,
        chain,
        name="scan",
        scan_info=None,
        save=True,
        save_images=None,
        scan_saving=None,
        watchdog_callback=None,
        scan_progress=None,
    ):
        """
        Scan class to publish data and trigger the writer if any.

        Arguments:
            chain: Acquisition chain you want to use for this scan.
            name: Scan name, if None set default name *scan*
            scan_info: Scan parameters if some, as a dict (or as ScanInfo
                       object)
            save: True if this scan have to be saved
            save_images: None means follows "save"
            scan_saving: Object describing how to save the scan, if any
            scan_progress: a ScanProgress instance
        """
        self.__name = name
        self.__scan_number = None
        self.__user_scan_meta = None
        self.__controllers_scan_meta = None
        self._scan_info = ScanInfo()

        self.__root_node = None
        self._scan_connection = None
        self._shadow_scan_number = not save

        nonsaved_ct = False
        if scan_info:
            nonsaved_ct = scan_info.get("type", None) == "ct" and not save
        self._add_to_scans_queue = not nonsaved_ct
        self._enable_scanmeta = not nonsaved_ct

        # Double buffer pipeline for streams store
        self._rotating_pipeline_mgr = None

        self.__nodes = dict()
        self._devices = []
        self._axes_in_scan = []  # for pre_scan, post_scan in axes hooks
        self._restore_motor_positions = False

        self._data_events = dict()
        self.set_watchdog_callback(watchdog_callback)

        self._scan_progress_task = None
        self._scan_progress = scan_progress

        self.__state = ScanState.IDLE
        self.__state_change = gevent.event.Event()
        self._preset_list = list()
        self.__node = None
        self.__comments = list()  # user comments

        # Independent scan initialization (order not important):
        self._init_acq_chain(chain)
        self._init_scan_saving(scan_saving)
        self._init_scan_display()

        # Dependent scan initialization (order is important):
        self._metadata_at_scan_instantiation(scan_info=scan_info, save=save)
        self._init_writer(save=save, save_images=save_images)
        self._init_flint()

    def _init_scan_saving(self, scan_saving):
        if scan_saving is None:
            scan_saving = current_session.scan_saving
        self.__scan_saving = scan_saving.clone()

    @property
    def scan_saving(self):
        return self.__scan_saving

    def _init_scan_display(self):
        self.__scan_display = current_session.scan_display.clone()

    def _init_acq_chain(self, chain):
        """Initialize acquisition chain"""
        self._acq_chain = chain
        self._check_acq_chan_unique_name()

    def _check_acq_chan_unique_name(self):
        """Make channel names unique in the scope of the scan"""
        names = []
        for node in self._acq_chain._tree.is_branch(self._acq_chain._tree.root):
            self._uniquify_chan_name(node, names)

    def _uniquify_chan_name(self, node, names):
        """Change the node's channel names in case of collision"""
        if node.channels:
            for c in node.channels:
                if c.name in names:
                    if self._acq_chain._tree.get_node(node).bpointer:
                        new_name = (
                            self._acq_chain._tree.get_node(node).bpointer.name
                            + ":"
                            + c.name
                        )
                    else:
                        new_name = c.name
                    if new_name in names:
                        new_name = str(id(c)) + ":" + c.name
                    c._AcquisitionChannel__name = new_name
                names.append(c.name)

        for node in self._acq_chain._tree.is_branch(node):
            self._uniquify_chan_name(node, names)

    def _init_writer(self, save=True, save_images=None):
        """Initialize the data writer if needed"""
        scan_config = self.__scan_saving.get()
        if save:
            self.__writer = scan_config["writer"]
        else:
            self.__writer = NullWriter(
                scan_config["root_path"],
                scan_config["images_path"],
                os.path.basename(scan_config["data_path"]),
            )
        self.__writer._save_images = save if save_images is None else save_images

    def _init_flint(self):
        """Initialize flint if needed"""
        if is_bliss_shell():
            scan_display = self.__scan_display
            if scan_display.auto:
                if self.is_flint_recommended():
                    plot_mdl.get_flint(
                        restart_if_stucked=scan_display.restart_flint_if_stucked,
                        mandatory=False,
                    )

    def is_flint_recommended(self):
        """Return true if flint is recommended for this scan"""
        scan_info = self._scan_info
        kind = scan_info.get("type", None)

        # If there is explicit plots, Flint is helpful
        plots = scan_info.get("plots", [])
        if len(plots) >= 1:
            return True

        # For ct, Flint is only recommended if there is MCAs or images
        if kind == "ct":
            chain = scan_info["acquisition_chain"]
            ndim_data = []
            for _top_master, chain in scan_info["acquisition_chain"].items():
                ndim_data.extend(chain.get("images", []))
                ndim_data.extend(chain.get("spectra", []))
                ndim_data.extend(chain.get("master", {}).get("images", []))
                ndim_data.extend(chain.get("master", {}).get("spectra", []))
            return len(ndim_data) > 0

        return True

    @property
    def _node_name(self):
        assert self.__scan_number is not None, "The scan number is not known yet"
        node_name = str(self.__scan_number) + "_" + self.name
        if self._shadow_scan_number:
            return "_" + node_name
        else:
            return node_name

    @property
    def root_node(self):
        if self.__root_node is None:
            self.__root_node = self.__scan_saving.get_parent_node()
        return self.__root_node

    def _create_scan_node(self):
        if self.__node is not None:
            raise RuntimeError("The scan node already exists")

        # Redis connection used byt scan node and its children.
        # Has client-side caching during the scan (disabled at the end).
        if self._REDIS_CACHING:
            self._scan_connection = get_redis_proxy(db=1, caching=True, shared=False)
        else:
            self._scan_connection = self.root_connection

        self.__node = create_node(
            self._node_name,
            node_type=self._NODE_TYPE,
            parent=self.root_node,
            info=self._scan_info,
            connection=self._scan_connection,
        )
        if self._REDIS_CACHING:
            self.__node.add_prefetch()

    @property
    def root_connection(self):
        """Redis connection of the root node (parent of the scan).
        Does not have client-side caching.

        :returns RedisDbProxy:
        """
        return self.root_node.db_connection

    def _disable_caching(self):
        """After this, the `scan_connection` behaves like a normal
        RedisDbProxy without caching
        """
        if self._REDIS_CACHING and self._scan_connection is not None:
            self._scan_connection.disable_caching()

    def set_expiration_time(self):
        """Set the expiration time of all Redis keys associated to this scan"""
        parent_db_names = self._get_parent_db_names()
        data_db_names = self._get_data_db_names()
        self.__scan_saving.set_expiration_time(data_db_names, parent_db_names)

    def _get_data_db_names(self) -> set:
        """Get all Redis keys associated to the children of this scan"""
        db_names = set()
        nodes = list(self.nodes.values())
        for node in nodes:
            db_names |= set(node.get_db_names(include_parents=False))
        return db_names

    def _get_parent_db_names(self) -> set:
        """Get all Redis keys associated to the scan and its parents"""
        return set(self.node.get_db_names(include_parents=True))

    def get_db_names(self) -> set:
        """Get all Redis keys associated to this scan"""
        names = set(self.node.get_db_names(include_parents=False))
        names |= self._get_data_db_names()
        return names

    def _init_scan_number(self):
        if self.__scan_number is not None:
            raise RuntimeError("The scan number can be initialized only once")
        self.writer.template.update(
            {
                "scan_name": self.name,
                "session": self.__scan_saving.session,
                "scan_number": "{scan_number}",
            }
        )
        self.__scan_number = self._next_scan_number()
        self.writer.template["scan_number"] = self.scan_number

    def _init_pipeline_mgr(self):
        # Channel data will be emitted and the associated `trigger_data_watch_callback`
        # calls executed, when one of the following things happens:
        #  - 1 stream has buffered a number of events equal to `max_stream_events`
        #  - the total buffered data has reached `max_bytes` bytes
        #  - the time from the first buffered event reached `max_time`
        #  - `flush` is called on the proxy rotation manager

        max_time = 0.2  # We don't want to keep Redis subscribers waiting too long
        if channelnode.CHANNEL_MAX_LEN:
            max_stream_events = min(channelnode.CHANNEL_MAX_LEN // 10, 50)
        else:
            max_stream_events = 50
        max_bytes = None  # No maximum

        self._rotating_pipeline_mgr = self.root_connection.rotating_pipeline(
            max_bytes=max_bytes, max_stream_events=max_stream_events, max_time=max_time
        )

    def _cleanup_pipeline_mgr(self):
        self._rotating_pipeline_mgr = None

    def __repr__(self):
        number = self.__scan_number
        if self._shadow_scan_number:
            number = ""
            path = "'not saved'"
        else:
            number = f"number={self.__scan_number}, "
            path = self.writer.filename

        return f"Scan({number}name={self.name}, path={path})"

    @property
    def name(self):
        return self.__name

    @property
    def state(self) -> ScanState:
        return self.__state

    @property
    def writer(self):
        return self.__writer

    @property
    def node(self):
        return self.__node

    @property
    def nodes(self):
        return self.__nodes

    @property
    def acq_chain(self):
        return self._acq_chain

    @property
    def scan_info(self):
        return self._scan_info

    @property
    def scan_number(self):
        if self.__scan_number:
            return self.__scan_saving.scan_number_format % self.__scan_number
        else:
            return "{scan_number}"

    @property
    def restore_motor_positions(self):
        """Weither to restore the initial motor positions at the end of scan run (for dscans)."""
        return self._restore_motor_positions

    @restore_motor_positions.setter
    def restore_motor_positions(self, restore):
        """Weither to restore the initial motor positions at the end of scan run (for dscans)."""
        self._restore_motor_positions = restore

    def get_plot(
        self, channel_item, plot_type, as_axes=False, wait=False, silent=False
    ):
        warnings.warn(
            "Scan.get_plot is deprecated, use bliss.common.plot.get_plot instead",
            DeprecationWarning,
        )
        return get_plot(
            channel_item,
            plot_type,
            scan=self,
            as_axes=as_axes,
            wait=wait,
            silent=silent,
        )

    @property
    def get_channels_dict(self):
        """A dictionary of all channels used in this scan"""
        return {c.name: c for n in self.acq_chain.nodes_list for c in n.channels}

    def add_preset(self, preset):
        """
        Add a preset for this scan
        """
        if not isinstance(preset, ScanPreset):
            raise ValueError("Expected ScanPreset instance")
        self._preset_list.append(preset)

    def set_watchdog_callback(self, callback):
        """
        Set a watchdog callback for this scan
        """
        if callback:
            self._watchdog_task = _WatchDogTask(self, callback)
        else:
            self._watchdog_task = None

    def _get_data_axes(self, include_calc_reals=False):
        """
        Return all axes objects in this scan

        Arguments:
        - include_calc_reals (bool or int): True -> get calc axes + real axes, False (default): do not return reals from calc

        If a positive integer is specified, it means real axes from calc ones are returned up to the specified depth
        """
        master_axes = []
        if isinstance(include_calc_reals, bool):
            calc_depth = -1 if include_calc_reals else 0
        else:
            calc_depth = include_calc_reals
        for node in self.acq_chain.nodes_list:
            if not isinstance(node, AcquisitionMaster):
                continue
            if isinstance(node.device, Axis):
                master_axes.append(node.device)
                master_axes += get_real_axes(node.device, depth=calc_depth)
            elif is_motor_group(node.device):
                master_axes += node.device.axes.values()
                master_axes += get_real_axes(
                    *node.device.axes.values(), depth=calc_depth
                )

        return master_axes

    def update_ctrl_params(self, ctrl, new_param_dict):
        if self.state != ScanState.IDLE:
            raise RuntimeError(
                "Scan state is not idle. ctrl_params can only be updated before scan starts running."
            )
        ctrl_acq_dev = None
        for acq_dev in self.acq_chain.nodes_list:
            if ctrl is acq_dev.device:
                ctrl_acq_dev = acq_dev
                break
        if ctrl_acq_dev is None:
            raise RuntimeError(f"Controller {ctrl} not part of this scan!")

        ## for Bliss 2 we have to see how to make acq_params available systematically
        potential_new_ctrl_params = ctrl_acq_dev.ctrl_params.copy()
        potential_new_ctrl_params.update(new_param_dict)

        # invoking the Validator here will only work if we have a
        # copy of initial acq_params in the acq_obj
        # ~ if hasattr(ctrl_acq_dev, "acq_params"):
        # ~ potential_new_ctrl_params = CompletedCtrlParamsDict(
        # ~ potential_new_ctrl_params
        # ~ )
        # ~ ctrl_acq_dev.validate_params(
        # ~ ctrl_acq_dev.acq_params, ctrl_params=potential_new_ctrl_params
        # ~ )

        # at least check that no new keys are added
        if set(potential_new_ctrl_params.keys()) == set(
            ctrl_acq_dev.ctrl_params.keys()
        ):
            ctrl_acq_dev.ctrl_params.update(new_param_dict)
        else:
            raise RuntimeError(f"New keys can not be added to ctrl_params of {ctrl}")

    def _get_x_y_data(self, counter, axis):
        data = self.get_data()
        x_data = data[axis]
        y_data = data[counter]
        return x_data, y_data

    def fwhm(self, counter, axis=None, return_axes=False):
        return self._multimotors(self._fwhm, counter, axis, return_axes=return_axes)

    def _fwhm(self, counter, axis=None):
        return scan_math.cen(*self._get_x_y_data(counter, axis))[1]

    def peak(self, counter, axis=None, return_axes=False):
        return self._multimotors(self._peak, counter, axis, return_axes=return_axes)

    def _peak(self, counter, axis):
        return scan_math.peak(*self._get_x_y_data(counter, axis))

    def trough(self, counter, axis=None, return_axes=False):
        return self._multimotors(self._trough, counter, axis, return_axes=return_axes)

    def _trough(self, counter, axis):
        return scan_math.trough(*self._get_x_y_data(counter, axis))

    def com(self, counter, axis=None, return_axes=False):
        return self._multimotors(self._com, counter, axis, return_axes=return_axes)

    def _com(self, counter, axis):
        return scan_math.com(*self._get_x_y_data(counter, axis))

    def cen(self, counter, axis=None, return_axes=False):
        return self._multimotors(self._cen, counter, axis, return_axes=return_axes)

    @typecheck
    def find_position(
        self,
        func: Callable[[Any, Any], float],
        counter: _countable,
        axis=None,
        return_axes=False,
    ):
        """evaluate user supplied scan math function"""

        def _find_custom(counter, axis):
            return func(*self._get_x_y_data(counter, axis))

        return self._multimotors(_find_custom, counter, axis, return_axes=return_axes)

    def _cen(self, counter, axis):
        return scan_math.cen(*self._get_x_y_data(counter, axis))[0]

    def _multimotors(self, func, counter, axis=None, return_axes=False):
        motors = self._get_data_axes()
        axes_names = [axis.name for axis in motors]
        res = collections.UserDict()

        def info():
            """TODO: could be a nice table at one point"""
            s = "{"
            for key, value in res.items():
                if len(s) != 1:
                    s += ", "
                s += f"{key.name}: {rounder(key.tolerance, value)}"
            s += "}"
            return s

        res.__info__ = info

        if axis is not None:
            if isinstance(axis, str):
                assert axis in axes_names or axis in ["elapsed_time", "epoch"]
            else:
                assert axis.name in axes_names
            res[axis] = func(counter, axis=axis)
        elif len(axes_names) == 1 and axes_names[0] in ["elapsed_time", "epoch"]:
            res = {axis: func(counter, axis=axes_names[0])}
        else:
            # allow "timer axis" for timescan
            if self.scan_info.get("type") in ["loopscan", "timescan"]:
                motors = ["elapsed_time"]
            if len(motors) < 1:
                raise RuntimeError("No axis found in this scan.")
            for mot in motors:
                res[mot] = func(counter, axis=mot)

        if not return_axes and len(res) == 1:
            return next(iter(res.values()))
        else:
            return res

    def _goto_multimotors(self, goto: Dict[Axis, float]):
        bad_pos = [(mot, pos) for mot, pos in goto.items() if not numpy.isfinite(pos)]
        if len(bad_pos) > 0:
            motors = ", ".join([mot.name for mot, pos in goto.items()])
            pos = [pos for mot, pos in goto.items()]
            pos = ", ".join(
                [(f"{p}" if numpy.isfinite(p) else f"{p} (bad)") for p in pos]
            )
            raise RuntimeError(f"Motor(s) move aborted. Request: {motors} -> {pos}")
        for key in goto.keys():
            if key in ["elapsed_time", "epoch"]:
                RuntimeError("Cannot move. Time travel forbidden.")
            assert not isinstance(key, str)
        with error_cleanup(
            *goto.keys(), restore_list=(cleanup_axis.POS,), verbose=True
        ):
            group = Group(*goto.keys())
            group.move(goto, wait=True, relative=False)

    def goto_peak(self, counter, axis=None):
        return self._goto_multimotors(self.peak(counter, axis, return_axes=True))

    def goto_min(self, counter, axis=None):
        return self._goto_multimotors(self.trough(counter, axis, return_axes=True))

    def goto_com(self, counter, axis=None, return_axes=False):
        return self._goto_multimotors(self.com(counter, axis, return_axes=True))

    def goto_cen(self, counter, axis=None, return_axes=False):
        return self._goto_multimotors(self.cen(counter, axis, return_axes=True))

    @typecheck
    def goto_custom(
        self,
        func: Callable[[Any, Any], float],
        counter: _countable,
        axis=None,
        return_axes=False,
    ):
        """goto for custom user supplied scan math function"""
        return self._goto_multimotors(
            self.find_position(func, counter, axis, return_axes=True)
        )

    def wait_state(self, state):
        while self.__state < state:
            self.__state_change.clear()
            self.__state_change.wait()

    def __trigger_watchdog_data_event(self, signal, sender):
        if self._watchdog_task is not None:
            self._watchdog_task.trigger_data_event(sender, signal)

    def _channel_event(self, event_dict, signal=None, sender=None):
        with KillMask():
            with self._rotating_pipeline_mgr.async_proxy() as async_proxy:
                self.nodes[sender].store(event_dict, cnx=async_proxy)
                async_proxy.add_execute_callback(
                    event.send, sender, "new_data_stored", event_dict
                )

                self.__trigger_watchdog_data_event(signal, sender)

    def _device_event(self, event_dict=None, signal=None, sender=None):
        if signal == "end":
            self._rotating_pipeline_mgr.flush(raise_error=False)
            self.__trigger_watchdog_data_event(signal, sender)

    def prepare(self, scan_info, devices_tree):
        self._prepare_devices(devices_tree)
        self.writer.prepare(self)

        # Publishes the metadata of a "prepared" scan
        # in Redis
        self._metadata_at_scan_prepared()
        self.node.prepared(self._scan_info)

        self._axes_in_scan = self._get_data_axes(include_calc_reals=True)
        with execute_pre_scan_hooks(self._axes_in_scan):
            pass

    def _prepare_devices(self, devices_tree):
        nodes = dict()
        # DEPTH expand without the root node
        devices = list(devices_tree.expand_tree())[1:]

        # Create channel nodes and their parents in Redis
        addparentinfo = dict()  # {level:(parents, children)}
        asynchelper = DataNodeAsyncHelper(self._scan_connection)

        with asynchelper:
            # All this will be executed in one pipeline:
            for dev in devices:
                if not isinstance(dev, (AcquisitionSlave, AcquisitionMaster)):
                    continue

                # Create the parent node for the channel nodes
                dev_node = devices_tree.get_node(dev)
                level = devices_tree.depth(dev_node)
                if level == 1:
                    # Top level node has the scan node as parent
                    parent = self.node
                else:
                    parent = nodes[dev_node.bpointer]
                channel_parent = create_node(
                    dev.name,  # appended to parent.db_name
                    parent=parent,
                    add_to_parent=False,  # post-pone because order matters
                    connection=asynchelper.async_proxy,
                )
                asynchelper.replace_connection(channel_parent)
                nodes[dev] = channel_parent

                parents, children = addparentinfo.setdefault(level, (list(), list()))
                parents.append((parent, channel_parent))

                # Create the channel nodes
                for channel in dev.channels:
                    channel_node = create_node(
                        channel.short_name,  # appended to channel_parent.db_name
                        node_type=channel.data_node_type,
                        parent=channel_parent,
                        add_to_parent=False,  # post-pone because order matters
                        shape=channel.shape,
                        dtype=channel.dtype,
                        unit=channel.unit,
                        fullname=channel.fullname,  # node.fullname
                        channel_name=channel.fullname,  # node.name
                        connection=asynchelper.async_proxy,
                    )
                    asynchelper.replace_connection(channel_node)
                    channel.data_node = channel_node
                    nodes[channel] = channel_node
                    children.append((channel_parent, channel_node))

        if self._REDIS_CACHING:
            for node in nodes.values():
                node.add_prefetch()

        # Add the children to their parents in Redis (NEW_NODE events)
        for level, addlists in sorted(addparentinfo.items(), key=lambda item: item[0]):
            for addlist in addlists:
                with asynchelper:
                    # All this will be executed in one pipeline:
                    for parent, child in addlist:
                        asynchelper.replace_connection(parent, child)
                        parent.add_children(child)

        # Connect device and channel events
        self.__nodes = nodes
        self._devices = devices
        for dev, node in list(nodes.items()):
            if dev in devices:
                event.connect(dev, "start", self._device_event)
                event.connect(dev, "end", self._device_event)
            else:
                event.connect(dev, "new_data", self._channel_event)

    def _metadata_at_scan_instantiation(self, scan_info=None, save=True):
        """Metadata of an "instantiated" scan. Saved in Redis when creating the scan node."""
        if scan_info is not None:
            self._scan_info.update(scan_info)
        scan_saving = self.__scan_saving
        self._scan_info.setdefault("title", self.__name)
        self._scan_info["session_name"] = scan_saving.session
        self._scan_info["user_name"] = scan_saving.user_name
        self._scan_info["data_writer"] = scan_saving.writer
        self._scan_info["writer_options"] = scan_saving.writer_options()
        self._scan_info["data_policy"] = scan_saving.data_policy
        self._scan_info["shadow_scan_number"] = self._shadow_scan_number
        self._scan_info["save"] = save
        self._scan_info["publisher"] = "Bliss"
        self._scan_info["publisher_version"] = publisher_version
        self._scan_info.set_acquisition_chain_info(self._acq_chain)

    def _metadata_at_scan_start(self):
        """Metadata of a "started" scan. Saved in Redis when creating the scan node.
        So this is the first scan_info any subscriber sees.
        """
        self._scan_info["scan_nb"] = self.__scan_number

        # this has to be done when the writer is ready
        self._scan_info["filename"] = self.writer.filename
        self._scan_info["images_path"] = self.writer.images_path(self)

        start_timestamp = time.time()
        start_time = datetime.datetime.fromtimestamp(start_timestamp)
        self._scan_info["start_time"] = start_time
        start_time_str = start_time.strftime("%a %b %d %H:%M:%S %Y")
        self._scan_info["start_time_str"] = start_time_str
        self._scan_info["start_timestamp"] = start_timestamp

        self._metadata_of_plot()

        self._metadata_of_acq_controllers(META_TIMING.START)
        self._metadata_of_nonacq_controllers(META_TIMING.START)
        self._metadata_of_user(META_TIMING.START)

    def _metadata_at_scan_prepared(self):
        """Metadata of a "prepared" scan. Saved in Redis by `ScanNode.prepared`"""
        self._metadata_of_acq_controllers(META_TIMING.PREPARED)
        self._metadata_of_nonacq_controllers(META_TIMING.PREPARED)
        self._metadata_of_user(META_TIMING.PREPARED)

    def _metadata_at_scan_end(self):
        """Metadata of a "finished" scan. Saved in Redis by `ScanNode.end`"""
        self._metadata_of_acq_controllers(META_TIMING.END)
        self._metadata_of_nonacq_controllers(META_TIMING.END)
        self._metadata_of_user(META_TIMING.END)

    def _metadata_of_plot(self):
        # Plot metadata
        display_extra = {}
        displayed_channels = self.__scan_display.displayed_channels
        if displayed_channels is not None:
            # Contextual display request
            display_extra["plotselect"] = displayed_channels
            if self.__scan_display._displayed_channels_time is not None:
                display_extra[
                    "plotselect_time"
                ] = self.__scan_display._displayed_channels_time
        displayed_channels = self.__scan_display._pop_next_scan_displayed_channels()
        if displayed_channels is not None:
            # Structural display request specified for this scan
            display_extra["displayed_channels"] = displayed_channels
        if len(display_extra) > 0:
            self._scan_info["_display_extra"] = display_extra

    def _metadata_of_user(self, timing):
        """Update scan_info with user scan metadata. The metadata will be
        stored in the user metadata categories.
        """
        if not self._enable_scanmeta:
            return
        self._evaluate_scan_meta(self._user_scan_meta, timing)

    def _metadata_of_nonacq_controllers(self, timing):
        """Update scan_info with controller scan metadata. The metadata
        will be stored in the "instrument" metadata category under the
        "scan_metadata_name" which is the controller name by default
        (see HasMetadataForScan).
        """
        if not self._enable_scanmeta:
            return
        self._evaluate_scan_meta(self._controllers_scan_meta, timing)

    def _metadata_of_acq_controllers(self, timing):
        """Update the controller Redis nodes with metadata. Update
        the "devices" section of scan_info. Note that the "instrument"
        metadata category or any other metadata category is not modified.
        """
        # Note: not sure why we disable the others but keep the
        #       metadata of the acquisition controllers.
        # if not self._enable_scanmeta:
        #    return

        if self._controllers_scan_meta:
            instrument = self._controllers_scan_meta.instrument
        else:
            instrument = None

        for acq_obj in self.acq_chain.nodes_list:
            # Controllers which implement the HasScanMetadata interface
            # will have their metadata already in scan_info.
            if instrument:
                if instrument.is_set(acq_obj):
                    continue

            # There is a difference between None and an empty dict.
            # An empty dict shows up as a group in the Nexus file
            # while None does not.
            with KillMask(masked_kill_nb=1):
                metadata = acq_obj.get_acquisition_metadata(timing=timing)
            if metadata is None:
                continue

            # Add to the local scan_info, but in a different
            # place than where _controllers_scan_meta would put it
            self._scan_info._set_device_meta(acq_obj, metadata)

    def _evaluate_scan_meta(self, scan_meta, timing):
        """Evaluate the metadata generators of a ScanMeta instance
        and update scan_info.
        """
        assert isinstance(scan_meta, ScanMeta)
        with KillMask(masked_kill_nb=1):
            metadata = scan_meta.to_dict(self, timing=timing)
            if not metadata:
                return
            deep_update(self._scan_info, metadata)
        original = set(self._scan_info.get("scan_meta_categories", []))
        extra = set(scan_meta.used_categories_names())
        self._scan_info["scan_meta_categories"] = list(original | extra)

    @property
    def _user_scan_meta(self):
        if self.__user_scan_meta is None and self._enable_scanmeta:
            self.__user_scan_meta = get_user_scan_meta().copy()
        return self.__user_scan_meta

    @property
    def _controllers_scan_meta(self):
        if self.__controllers_scan_meta is None and self._enable_scanmeta:
            self.__controllers_scan_meta = get_controllers_scan_meta()
        return self.__controllers_scan_meta

    def disconnect_all(self):
        for dev in self._devices:
            if isinstance(dev, (AcquisitionSlave, AcquisitionMaster)):
                for channel in dev.channels:
                    event.disconnect(channel, "new_data", self._channel_event)
                for signal in ("start", "end"):
                    event.disconnect(dev, signal, self._device_event)
        self._devices = []

    def _set_state(self, state):
        """Set the scan state"""
        if self.__state < state:
            self.__state = state
            if self.node is not None:
                # node can be None if the state change happens before
                # the node is constructed (in case of error for example)
                self.node.info["state"] = str(state)
            self._scan_info["state"] = str(state)
            self.__state_change.set()

    def add_comment(self, comment):
        """
        Adds a comment (string + timestamp) to scan_info that will also be
        saved in the file data file together with the scan
        """
        assert isinstance(comment, str)

        if self.__state < ScanState.DONE:
            self.__comments.append({"timestamp": time.time(), "message": comment})
            self._scan_info["comments"] = self.__comments
            if self.__state != ScanState.IDLE:
                self.node._info.update({"comments": self.__comments})
        else:
            raise RuntimeError(
                "Comments can only be added to scans that have not terminated!"
            )

    @property
    def comments(self):
        """
        list of comments that have been attacht to this scan by the user
        """
        return self.__comments

    def get_data(self, key=None):
        """Return a dictionary of { channel_name: numpy array }.

        It is a 1D array corresponding to the scan points.
        Each point is a named structure corresponding to the counter names.
        """

        class DataContainer(dict):
            def __info__(self):
                return f"DataContainer uses a key [counter], [motor] or [name_pattern] matching one of these names:\n {list(self.keys())}"

            def __getitem__(self, key):
                if isinstance(key, Counter):
                    return super().__getitem__(key.fullname)
                elif isinstance(key, Axis):
                    return super().__getitem__(f"axis:{key.name}")

                try:  # maybe a fullname
                    return super().__getitem__(key)

                except KeyError:

                    # --- maybe an axis (comes from config so name is unique)
                    axname = f"axis:{key}"
                    if axname in self.keys():
                        return super().__getitem__(axname)

                    # --- else check if it can match one of the DataContainer keys
                    matches = get_matching_names(
                        key, self.keys(), strict_pattern_as_short_name=True
                    )[key]

                    if len(matches) > 1:
                        raise KeyError(
                            f"Ambiguous key '{key}', there are several matches -> {matches}"
                        )

                    elif len(matches) == 1:
                        return super().__getitem__(matches[0])

                    else:
                        msg = "%s not found, try one of those %s" % (
                            key,
                            [x.split(":")[-1] for x in self.keys()],
                        )
                        raise KeyError(msg)

        data = DataContainer()
        try:
            # Gathering data from Redis can fail because of stream time-to-live, but
            # also because of trimming when streams reach their maximum specified length.
            pipeline = self.node.db_connection.pipeline()
            for channel_name, channel_data in get_data_from_nodes(
                pipeline, *self.nodes.values()
            ):
                data[channel_name] = channel_data
        except RedisDataExpiredError:
            if not self.scan_info["save"]:
                raise RuntimeError(
                    "Unsaved scan have expired on Redis, please use saved scans for later access."
                )
            else:
                with dynamic_hdf5.File(
                    self.scan_info["filename"], retry_timeout=0, retry_period=0
                ) as nxroot:
                    for channel in self.get_channels_dict.values():
                        data_path = f"{scan_utils.scan_name(self)}/measurement/{channel.fullname}"
                        data[channel.fullname] = numpy.array(nxroot[data_path])

        if key:
            return data[key]
        else:
            return data

    def _next_scan_number(self):
        SCAN_NUMBER_KEY = "last_scan_number"
        if self._shadow_scan_number:
            SCAN_NUMBER_KEY = "last_shadow_scan_number"
        filename = self.writer.filename
        # last scan number is stored in the parent of the scan
        parent_db_name = self.root_node.db_name
        cnx = self.root_connection
        with self.SCAN_NUMBER_LOCK:
            last_scan_number = cnx.hget(parent_db_name, SCAN_NUMBER_KEY)
            if (
                not self._shadow_scan_number
                and last_scan_number is None
                and "{scan_number}" not in filename
            ):
                # next scan number from the file (1 when not existing)
                next_scan_number = self.writer.last_scan_number + 1
                cnx.hsetnx(parent_db_name, SCAN_NUMBER_KEY, next_scan_number)
            else:
                # next scan number from Redis
                next_scan_number = cnx.hincrby(parent_db_name, SCAN_NUMBER_KEY, 1)
            return next_scan_number

    def _execute_preset(self, method_name):
        preset_tasks = [
            gevent.spawn(getattr(preset, method_name), self)
            for preset in self._preset_list
        ]
        try:
            gevent.joinall(preset_tasks, raise_error=True)
        except BaseException:
            gevent.killall(preset_tasks)
            raise

    def run(self):
        if self.state != ScanState.IDLE:
            raise RuntimeError(
                "Scan state is not idle. Scan objects can only be used once."
            )

        with ExitStack() as cstack:
            # Perpare error capturing. This needs to be the first
            # context in the stack.
            ctx = capture_exceptions(raise_index=0)
            capture = cstack.enter_context(ctx)
            capture = self._capture_with_error_mapping(capture)
            cstack.enter_context(capture())

            def add_context(ctx):
                # Ensures that context enter exceptions are always
                # captured before context exit exceptions
                yielded_value = cstack.enter_context(ctx)
                cstack.enter_context(capture())
                return yielded_value

            # A stack of context managers before running the actual
            # scan loop:

            ctx = self._runctx_before_scan_state(capture)
            add_context(ctx)

            ctx = self._runctx_scan_state(capture)
            add_context(ctx)

            if self.restore_motor_positions:
                ctx = self._runctx_motor_positions(capture)
                add_context(ctx)

            ctx = self._runctx_scan_saving(capture)
            add_context(ctx)

            ctx = self._runctx_scan_node(capture)
            add_context(ctx)

            ctx = self._runctx_pipeline_mgr(capture)
            add_context(ctx)

            if self._watchdog_task is not None:
                ctx = self._runctx_watchdog(capture)
                add_context(ctx)

                ctx = self._runctx_watchdog_callback(capture)
                add_context(ctx)

            if self._scan_progress is not None:
                ctx = self._runctx_scan_progress(capture)
                add_context(ctx)

            # NB: "user_print" messages won't be displayed to stdout, this avoids
            # output like "moving from X to Y" on motors for example. In principle
            # there should be no output to stdout from the scan itself.
            ctx = disable_user_output()
            add_context(ctx)

            # The actually scan loop
            ctx = self._runctx_scan_runner(capture)
            runner = add_context(ctx)
            self._execute_scan_runner(runner)

    def _execute_scan_runner(self, runner):
        # get scan iterators
        # be careful: this has to be done after "scan_new" callback,
        # since it is possible to add presets in the callback...
        scan_chain_iterators = [next(i) for i in self.acq_chain.get_iter_list()]

        # prepare acquisition objects (via AcquisitionChainIter)
        runner.send([gevent.spawn(i.apply_parameters) for i in scan_chain_iterators])

        self._set_state(ScanState.PREPARING)

        self._execute_preset("_prepare")

        self.prepare(self.scan_info, self.acq_chain._tree)

        runner.send(
            [
                gevent.spawn(i.prepare, self, self.scan_info)
                for i in scan_chain_iterators
            ]
        )

        self._set_state(ScanState.STARTING)

        self._execute_preset("start")

        runner.send((self, scan_chain_iterators, self._watchdog_task))

        self._set_state(ScanState.STOPPING)

        runner.send(
            [gevent.spawn(i.stop) for i in scan_chain_iterators if i is not None]
        )

    def _capture_with_error_mapping(self, capture):
        """Error mapping:
        - KeyboardInterrupt -> ScanAbort
        """

        @functools.wraps(capture)
        def wrapper():
            with capture():
                try:
                    yield
                except KeyboardInterrupt as e:
                    raise ScanAbort from e

        return contextmanager(wrapper)

    @contextmanager
    def _runctx_scan_state(self, capture):
        try:
            yield
        finally:
            with capture():
                if capture.failed:
                    _, first_error, _ = capture.failed[0]  # sys.exec_info()
                    if isinstance(first_error, (KeyboardInterrupt, ScanAbort)):
                        self._set_state(ScanState.USER_ABORTED)
                    else:
                        self._set_state(ScanState.KILLED)
                else:
                    self._set_state(ScanState.DONE)

    @contextmanager
    def _runctx_motor_positions(self, capture):
        first_level_scan_axes = self._get_data_axes()
        motor_positions = []
        for mot in self._get_data_axes(include_calc_reals=1):
            if mot not in first_level_scan_axes or not isinstance(mot, CalcAxis):
                pos = mot._set_position
                if not numpy.isnan(
                    pos
                ):  # exclude axes with Nan position (see issue #3762)
                    motor_positions.append((mot, pos))
        try:
            yield
        finally:
            with capture():
                if is_bliss_shell():
                    from bliss.shell.standard import _umove as move
                else:
                    from bliss.common.standard import _move as move
                move(motor_positions)

    @contextmanager
    def _runctx_scan_progress(self, capture):
        self._scan_progress.on_scan_new(self, self.scan_info)
        self._scan_progress_task = gevent.spawn(self._scan_progress.progress_task)
        try:
            yield
        finally:
            with capture():
                if self._scan_progress_task.ready():
                    if not self._scan_progress_task.successful():
                        self._scan_progress_task.get()
                else:
                    self._scan_progress_task.kill()
                self._scan_progress.on_scan_end(self.scan_info)

    @contextmanager
    def _runctx_watchdog(self, capture):
        self._watchdog_task.start()
        try:
            yield
        finally:
            with capture():
                self._watchdog_task.kill()

    @contextmanager
    def _runctx_watchdog_callback(self, capture):
        self._watchdog_task.on_scan_new(self, self.scan_info)
        try:
            yield
        finally:
            with capture():
                self._watchdog_task.on_scan_end(self.scan_info)

    @contextmanager
    def _runctx_scan_saving(self, capture):
        self._init_scan_number()
        self.__scan_saving.on_scan_run(not self._shadow_scan_number)
        try:
            yield
        finally:
            with capture():
                self.writer.finalize_scan_entry(self)
            with capture():
                self.writer.close()

    @contextmanager
    def _runctx_scan_node(self, capture):
        self._metadata_at_scan_start()
        self._create_scan_node()
        try:
            yield
        finally:
            with capture():
                self._metadata_at_scan_end()

            with capture():
                if capture.failed:
                    exception, _, _ = capture.failed[0]  # sys.exec_info()
                    exception = str(exception)
                else:
                    exception = ""
                self.node.end(self._scan_info, exception=exception)

            with capture():
                self.set_expiration_time()

            with capture():
                self._disable_caching()

    @contextmanager
    def _runctx_pipeline_mgr(self, capture):
        self._init_pipeline_mgr()
        try:
            yield
        finally:
            with capture():
                self._cleanup_pipeline_mgr()

    @contextmanager
    def _runctx_scan_runner(self, capture):
        try:
            yield _ScanIterationsRunner()
        finally:
            with capture():
                # Wait until all data has been published
                self._rotating_pipeline_mgr.flush(raise_error=True)

            with capture():
                self.disconnect_all()

            with capture():
                for node in self.nodes.values():
                    with capture():
                        try:
                            node.close()
                        except AttributeError:
                            pass

            with capture():
                self._execute_preset("_stop")

    @contextmanager
    def _runctx_before_scan_state(self, capture):
        """Pre and post actions that do not affect the Scan state"""
        try:
            yield
        finally:
            with capture():
                hooks = group_hooks(self._axes_in_scan)
                for hook in reversed(list(hooks)):
                    with capture():
                        hook.post_scan(self._axes_in_scan[:])

            with capture():
                if self._add_to_scans_queue:
                    current_session.scans.append(self)
