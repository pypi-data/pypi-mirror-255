# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import time
import numpy
import gevent
import gevent.event
import typing
import logging

from blissdata.beacon.data import BeaconData
from blissdata.redis_engine.store import DataStore
from blissdata.redis_engine.scan import Scan as RedisScan
from blissdata.redis_engine.scan import ScanState
from blissdata.redis_engine.stream import StreamingClient
from blissdata.lima.client import lima_client_factory
from blissdata.redis_engine.exceptions import NoScanAvailable, EndOfStream

if typing.TYPE_CHECKING:
    from blissdata.lima.client import LimaClientInterface

_logger = logging.getLogger(__name__)


_SLEEP_AT_START = 0.1
"""
Sleep done at the START event to allow other greenlets (other scan listeners)
to flush there data.

This allow to close already terminated scans before starting this new one.
And try to respect the sequenciality of scan events.

FIXME: It's fragile, and should be implemented in a different way.

See https://gitlab.esrf.fr/bliss/bliss/-/issues/4049
"""


class ScansObserver:
    """
    Observer for the `ScansWatcher`.

    Provides methods which can be inherited to follow the life cycle of the
    scans of a session.
    """

    def on_scan_created(self, scan_key: str, scan_info: dict):
        """
        Called upon scan created (devices are not yet prepared).

        Arguments:
            scan_key: Identifier of the scan
            scan_info: Dictionary containing scan metadata
        """
        pass

    def on_scan_started(self, scan_key: str, scan_info: dict):
        """
        Called upon scan started (the devices was prepared).

        Arguments:
            scan_key: Identifier of the scan
            scan_info: Dictionary containing scan metadata updated with metadata
                       prepared metadata from controllers
        """
        pass

    def on_scalar_data_received(
        self,
        scan_key: str,
        channel_name: str,
        index: int,
        data_bunch: typing.Union[list, numpy.ndarray],
    ):
        """
        Called upon a bunch of scalar data (0dim) from a `top_master` was
        received.

        Arguments:
            scan_key: Identifier of the parent scan
            channel_name: Name of the updated channel
            index: Start index of the data bunch in the real data stream.
                   There could be wholes between 2 bunches of data.
            data_bunch: The list of data received, as a bunch of data.
        """
        pass

    def on_ndim_data_received(
        self,
        scan_key: str,
        channel_name: str,
        dim: int,
        index: int,
        data_bunch: typing.Union[list, numpy.ndarray],
    ):
        """Called upon a ndim data (except 0dim, except data ref) data was
        received.

        - For 0dim data, see `on_scalar_data_received`.

        Arguments:
            scan_key: Identifier of the parent scan
            channel_name: Name of the channel emitting the data
            dim: Dimension of this data (MCA is 1, image is 2)
            index: Start index of the data bunch in the real data stream.
                   There could be wholes between 2 bunches of data.
            data_bunch: The list of data received, as a bunch of data.
        """
        pass

    def on_lima_event_received(
        self,
        scan_key: str,
        channel_name: str,
        last_index: int,
        lima_client: LimaClientInterface,
    ):
        """Called upon a ndim (except 0dim) data was received.

        For 0dim data, see `on_scalar_data_received`.

        Arguments:
            scan_key: Identifier of the parent scan
            channel_name: Name of the channel emitting the data
            last_index: last frame available in the lima_client
            lima_client: client to query images from
        """
        pass

    def on_scan_finished(self, scan_key: str, scan_info: dict):
        """
        Called upon scan end.

        Arguments:
            scan_key: Identifier of the parent scan
            scan_info: Dictionary containing scan metadata updated with
                       prepared and finished metadata from controllers
                       Other fields like positioners and datetime are also
                       updated.
        """
        pass


class ScansWatcher:
    """
    Watch scans from a specific session.

    Arguments:
        session_name: Name of the BLISS session
    """

    def __init__(self, session_name: str):
        self._session_name = session_name
        self._watch_scan_group = False
        self._observer: ScansObserver | None = None
        self._running: bool = False
        self._blocked: bool = False
        self._greenlet: gevent.Greenlet | None = None
        self._scan_watchers: list[ScanWatcher] = []
        self._data_store: DataStore | None = None

    def set_data_store(self, data_store: DataStore):
        """Define a DataStore to be used, else a default one will be created"""
        assert not self._running
        self._data_store = data_store

    def set_watch_scan_group(self, watch: bool):
        """
        Set to True to include scan groups like any other scans. Default is False.

        It have to be set before start.
        """
        assert not self._running
        self._watch_scan_group = watch

    def set_observer(self, observer: ScansObserver):
        """
        Set the observer to use with this watcher process.

        If not set, the `run` method will raise an exception.
        """
        assert not self._running
        self._observer = observer

    def stop(self, wait_running_scans=True):
        self._running = False
        if self._greenlet is not None:
            if self._blocked:
                self._greenlet.kill()
        for watcher in self._scan_watchers:
            if wait_running_scans:
                watcher.join()
            else:
                watcher.stop()
            self._scan_watchers = []
        if self._greenlet is not None:
            self._greenlet.join()

    def run(self):  # ignore_running_scans=True):
        """
        Run watching scan events.

        This method is blocking. But can be terminated by calling `stop`.

        Any scan node that is created before the `ready_event` will not be watched
        when `exclude_existing_scans` is True.
        """
        assert not self._running
        self._greenlet = gevent.getcurrent()
        self._running = True

        if self._observer is None:
            raise RuntimeError("No observer was set")

        # TODO use data_store.search_existing_scans() to collect already running scans

        since = None

        if self._data_store is not None:
            data_store = self._data_store
        else:
            redis_url = BeaconData().get_redis_data_db()
            data_store = DataStore(redis_url)

        while self._running:
            try:
                self._blocked = True
                since, scan_key = data_store.get_next_scan(since=since)
            except NoScanAvailable:
                continue
            finally:
                self._blocked = False

            scan = data_store.load_scan(scan_key, RedisScan)
            # TODO need helper to check session_name without opening Scan or use filter args on get_next_scan
            if scan.session != self._session_name:
                continue
            if not self._watch_scan_group and scan.info.get("is_scan_sequence", False):
                continue

            self._observer.on_scan_created(scan.key, scan.info)

            watcher = ScanWatcher(self._observer, scan)
            watcher.start()
            self._scan_watchers.append(watcher)


class ScanWatcher:
    """Watcher of a single scan"""

    def __init__(self, observer, scan):
        self._observer = observer
        self._scan = scan

        self._running = False
        self._blocked_on_state = False
        self._blocked_on_data = False

        self._state_greenlet: gevent.Greenlet | None = None
        self._data_greenlet: gevent.Greenlet | None = None

    def start(self):
        assert not self._running
        self._running = True
        self._state_greenlet = gevent.spawn(self._listen_state)
        self._state_greenlet.link_exception(self._log_greenlet_exception)

    def _listen_state(self):
        # Assume scan was CREATED recently.
        # IMPORTANT: This won't be true anymore if we search for already running scans when starting.
        prev_state = ScanState.CREATED

        while self._running:
            if prev_state < ScanState.STARTED <= self._scan.state:
                if _SLEEP_AT_START:
                    gevent.sleep(_SLEEP_AT_START)
                self._observer.on_scan_started(self._scan.key, self._scan.info)
                self._data_greenlet = gevent.spawn(self._listen_streams)
                self._data_greenlet.link_exception(self._log_greenlet_exception)

            if prev_state < ScanState.CLOSED <= self._scan.state:
                # make sure all data is read before advertising then end of the scan
                if self._data_greenlet is not None:
                    self._data_greenlet.join()
                self._observer.on_scan_finished(self._scan.key, self._scan.info)
                break

            prev_state = self._scan.state
            try:
                self._blocked_on_state = True
                self._scan.update()
            finally:
                self._blocked_on_state = False

    def _listen_streams(self):
        lima_clients = {}
        for stream in self._scan.streams.values():
            try:
                lima_clients[stream.key] = lima_client_factory(
                    self._scan._data_store, stream.info
                )
            except ValueError:
                pass

        client = StreamingClient(self._scan.streams)

        update_period = 0.1
        while self._running:
            try:
                self._blocked_on_data = True
                data = client.read()
            except EndOfStream:
                break
            finally:
                self._blocked_on_data = False

            for stream, entries in data.items():
                if stream.key in lima_clients:
                    _, lima_status = entries
                    lima_client = lima_clients[stream.key]
                    lima_client.update(**lima_status[-1])
                    self._observer.on_lima_event_received(
                        self._scan.key,
                        stream.name,
                        len(lima_client) - 1,
                        lima_client,
                    )
                elif stream.encoding["type"] == "numeric":
                    ndim = len(stream.encoding["shape"])
                    if ndim == 0:
                        index, data_bunch = entries
                        self._observer.on_scalar_data_received(
                            self._scan.key, stream.name, index, data_bunch
                        )
                    elif ndim == 1:
                        index, data_bunch = entries
                        self._observer.on_ndim_data_received(
                            self._scan.key, stream.name, ndim, index, data_bunch
                        )
                    else:
                        raise NotImplementedError(
                            "Don't know how to handle non-lima data with dim>1"
                        )
                # else:
                #     unhandled data types like scan sequences

            # Limiting update rate.
            # IMPORTANT: This is not a polling loop. Calls to client.read() only return
            # when new data is available, but new data can be available very frequently.
            time.sleep(update_period)

    def stop(self):
        self._running = False
        if self._state_greenlet is not None:
            if self._blocked_on_state:
                self._state_greenlet.kill()
        if self._data_greenlet is not None:
            if self._blocked_on_data:
                self._data_greenlet.kill()
        self.join()

    def join(self):
        gevent.joinall(list(filter(None, (self._state_greenlet, self._data_greenlet))))

    def _log_greenlet_exception(self, greenlet):
        try:
            greenlet.get()
        except Exception:
            _logger.exception(f"ScanWatcher greenlet {greenlet} failed.")
