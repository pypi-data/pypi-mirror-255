# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides helper to read scan_info.
"""
from __future__ import annotations
from typing import NamedTuple
from ..model import scan_model

import logging


_logger = logging.getLogger(__name__)


class ChannelInfo(NamedTuple):
    name: str
    info: dict[str, object] | None
    device: str | None
    master: str | None


def _get_channels(
    scan_info: dict,
    top_master_name: str | None = None,
    dim: int | None = None,
    master: bool | None = None,
):
    """
    Returns channels from top_master_name and optionally filtered by dim and master.

    Channels from masters are listed first, and the channel order stays the same.

    Arguments:
        scan_info: Scan info dict
        top_master_name: If not None, a specific top master is read
        dim: If not None, only includes the channels with the requested dim
        master: If not None, only includes channels from a master / or not
    """
    names = []

    master_count = 0
    for top_master, meta in scan_info["acquisition_chain"].items():
        if top_master_name is not None:
            if top_master != top_master_name:
                # If the filter mismatch
                continue
        devices = meta["devices"]
        for device_name in devices:
            device_info = scan_info["devices"].get(device_name, None)
            if device_info is None:
                continue

            if master is not None:
                is_triggering = "triggered_devices" in device_info
                if is_triggering:
                    master_count += 1
                is_master = is_triggering and master_count == 1
                if master ^ is_master:
                    # If the filter mismatch
                    continue

            for c in device_info.get("channels", []):
                if dim is not None:
                    if scan_info["channels"].get(c, {}).get("dim", 0) != dim:
                        # If the filter mismatch
                        continue
                names.append(c)

    return names


def iter_channels(scan_info: dict[str, object]):
    acquisition_chain_description = scan_info.get("acquisition_chain", {})
    assert isinstance(acquisition_chain_description, dict)
    channels_description = scan_info.get("channels", {})
    assert isinstance(channels_description, dict)

    def _get_device_from_channel_name(channel_name):
        """Returns the device name from the channel name, else None"""
        if ":" in channel_name:
            return channel_name.rsplit(":", 1)[0]
        return None

    channels = set([])

    for master_name in acquisition_chain_description.keys():
        master_channels = _get_channels(scan_info, master_name)
        for channel_name in master_channels:
            info = channels_description.get(channel_name, {})
            device_name = _get_device_from_channel_name(channel_name)
            channel = ChannelInfo(channel_name, info, device_name, master_name)
            yield channel
            channels.add(channel_name)

    requests = scan_info.get("channels", {})
    if not isinstance(requests, dict):
        _logger.warning("scan_info.requests is not a dict")
        requests = {}

    for channel_name, info in requests.items():
        if channel_name in channels:
            continue
        device_name = _get_device_from_channel_name(channel_name)
        # FIXME: For now, let say everything is scalar here
        channel = ChannelInfo(channel_name, info, device_name, "custom")
        yield channel


def _pop_and_convert(meta, key, func):
    value = meta.pop(key, None)
    if value is None:
        return None
    try:
        value = func(value)
    except ValueError:
        _logger.warning("%s %s is not a valid value. Field ignored.", key, value)
        value = None
    return value


def parse_channel_metadata(meta: dict) -> scan_model.ChannelMetadata:
    meta = meta.copy()

    # Link from channels to device
    # We can skip it
    meta.pop("device", None)

    # Compatibility Bliss 1.0
    if "axes-points" in meta and "axis_points" not in meta:
        _logger.warning("Metadata axes-points have to be replaced by axis_points.")
        meta["axis_points"] = meta.pop("axes-points")
    if "axes-kind" in meta and "axis_kind" not in meta:
        _logger.warning("Metadata axes-kind have to be replaced by axis_kind.")
        meta["axis_kind"] = meta.pop("axes-kind")

    start = _pop_and_convert(meta, "start", float)
    stop = _pop_and_convert(meta, "stop", float)
    vmin = _pop_and_convert(meta, "min", float)
    vmax = _pop_and_convert(meta, "max", float)
    points = _pop_and_convert(meta, "points", int)
    axisPoints = _pop_and_convert(meta, "axis_points", int)
    axisPointsHint = _pop_and_convert(meta, "axis_points_hint", int)
    axisKind = _pop_and_convert(meta, "axis_kind", scan_model.AxisKind)
    axisId = _pop_and_convert(meta, "axis_id", int)
    group = _pop_and_convert(meta, "group", str)
    dim = _pop_and_convert(meta, "dim", int)
    decimals = _pop_and_convert(meta, "decimals", int)

    # Compatibility code with existing user scripts written for BLISS 1.4
    mapping = {
        scan_model.AxisKind.FAST: (0, scan_model.AxisKind.FORTH),
        scan_model.AxisKind.FAST_BACKNFORTH: (0, scan_model.AxisKind.BACKNFORTH),
        scan_model.AxisKind.SLOW: (1, scan_model.AxisKind.FORTH),
        scan_model.AxisKind.SLOW_BACKNFORTH: (1, scan_model.AxisKind.BACKNFORTH),
    }
    if axisKind in mapping:
        if axisId is not None:
            _logger.warning(
                "Both axis_id and axis_kind with flat/slow is used. axis_id will be ignored"
            )
        axisId, axisKind = mapping[axisKind]

    for key in meta.keys():
        _logger.warning("Metadata key %s is unknown. Field ignored.", key)

    return scan_model.ChannelMetadata(
        start,
        stop,
        vmin,
        vmax,
        points,
        axisId,
        axisPoints,
        axisKind,
        group,
        axisPointsHint,
        dim,
        decimals,
    )
