# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import h5py
import numpy
import logging
from bliss.controllers.lima import roi as lima_rois
from bliss.flint.widgets.utils import rois as flint_rois
from silx.gui.plot.items import roi as silx_rois

_logger = logging.getLogger(__name__)


def _readRoi(roiName, h5Node):
    selection = h5Node.get("selection")
    if selection is None:
        raise ValueError("No 'selection' group available")
    kind = selection["kind"][()].decode("ascii")
    if kind == "rect":
        x = selection["x"][()]
        y = selection["y"][()]
        width = selection["width"][()]
        height = selection["height"][()]
        return lima_rois.Roi(x, y, width, height, roiName)
    elif kind == "arc":
        cx = selection["cx"][()]
        cy = selection["cy"][()]
        a1 = selection["a1"][()]
        a2 = selection["a2"][()]
        r1 = selection["r1"][()]
        r2 = selection["r2"][()]
        return lima_rois.ArcRoi(cx, cy, r1, r2, a1, a2, roiName)
    elif kind == "profile":
        mode = selection["mode"][()].decode("ascii")
        x = selection["x"][()]
        y = selection["y"][()]
        width = selection["width"][()]
        height = selection["height"][()]
        return lima_rois.RoiProfile(x, y, width, height, mode, roiName)
    else:
        raise RuntimeError(f"Unsupported ROI kind {kind}")


def readRoisFromHdf5(filename, path, detectorName):
    result = []
    with h5py.File(filename, "r") as hroot:
        if hroot.attrs["creator"] != "Bliss":
            raise RuntimeError("This file was not created by BLISS")

        if path not in hroot:
            raise RuntimeError(f"This file does not contain the expected {path} path")

        hscan = hroot[path]
        if hscan.attrs["NX_class"] != "NXentry":
            raise RuntimeError(f"The selected path {path} is not a scan")

        hdet = hscan.get(f"instrument/{detectorName}")
        if hdet is None:
            raise RuntimeError(f"The selected scan does not contain any {detectorName}")

        prefix = f"{detectorName}_"
        for name, node in hscan["instrument"].items():
            if name.startswith(prefix):
                roiName = name[len(prefix) :]
                try:
                    roi = _readRoi(roiName, node)
                except Exception:
                    _logger.error("ROI %s not readable", roiName, exc_info=True)
                else:
                    result.append(roi)

    return result


def limaRoiToScanRoi(roi):
    """FIXME: This have to be merged with `roiToGui`"""
    if isinstance(roi, lima_rois.RoiProfile):
        # Must be checked first as a RoiProfile is a RectRoi
        if roi.mode == "vertical":
            item = flint_rois.LimaVProfileRoi()
        elif roi.mode == "horizontal":
            item = flint_rois.LimaHProfileRoi()
        else:
            item = silx_rois.RectangleROI()
        origin = roi.x, roi.y
        size = roi.width, roi.height
        item.setGeometry(origin=origin, size=size)
    elif isinstance(roi, lima_rois.Roi):
        item = silx_rois.RectangleROI()
        origin = roi.x, roi.y
        size = roi.width, roi.height
        item.setGeometry(origin=origin, size=size)
    elif isinstance(roi, lima_rois.ArcRoi):
        item = silx_rois.ArcROI()
        center = roi.cx, roi.cy
        item.setGeometry(
            center=center,
            innerRadius=roi.r1,
            outerRadius=roi.r2,
            startAngle=numpy.deg2rad(roi.a1),
            endAngle=numpy.deg2rad(roi.a2),
        )
    else:
        item = None
    return item


def roiToGui(shape):
    if isinstance(shape, dict):
        kind = shape["kind"].lower()
        assert kind == "rectangle"
        x, y = map(int, map(round, shape["origin"]))
        w, h = map(int, map(round, shape["size"]))
        roi = silx_rois.RectangleROI()
        roi.setGeometry(origin=(x, y), size=(w, h))
        roi.setName(shape["label"])
    elif isinstance(shape, lima_rois.RoiProfile):
        if shape.mode == "horizontal":
            roi = flint_rois.LimaHProfileRoi()
        elif shape.mode == "vertical":
            roi = flint_rois.LimaVProfileRoi()
        else:
            _logger.error("RoiProfile mode '%s' unsupported", roi.mode)
            return None
        roi.setGeometry(origin=(shape.x, shape.y), size=(shape.width, shape.height))
        roi.setName(shape.name)
    elif isinstance(shape, lima_rois.Roi):
        roi = flint_rois.LimaRectRoi()
        roi.setGeometry(origin=(shape.x, shape.y), size=(shape.width, shape.height))
        roi.setName(shape.name)
    elif isinstance(shape, lima_rois.ArcRoi):
        roi = flint_rois.LimaArcRoi()
        roi.setGeometry(
            center=(shape.cx, shape.cy),
            innerRadius=shape.r1,
            outerRadius=shape.r2,
            startAngle=numpy.deg2rad(shape.a1),
            endAngle=numpy.deg2rad(shape.a2),
        )
        roi.setName(shape.name)
    else:
        roi = None
    return roi


def guiToRoi(roi):
    if isinstance(roi, silx_rois.RectangleROI):
        x, y = roi.getOrigin()
        w, h = roi.getSize()
        name = roi.getName()
        if isinstance(roi, flint_rois.LimaHProfileRoi):
            mode = "horizontal"
            shape = lima_rois.RoiProfile(x, y, w, h, mode=mode, name=name)
        elif isinstance(roi, flint_rois.LimaVProfileRoi):
            mode = "vertical"
            shape = lima_rois.RoiProfile(x, y, w, h, mode=mode, name=name)
        elif isinstance(roi, flint_rois.LimaRectRoi):
            shape = lima_rois.Roi(x, y, w, h, name=name)
        else:
            shape = dict(kind="Rectangle", origin=(x, y), size=(w, h), label=name)
    elif isinstance(roi, flint_rois.LimaArcRoi):
        cx = roi.getCenter()[0]
        cy = roi.getCenter()[1]
        r1 = roi.getInnerRadius()
        r2 = roi.getOuterRadius()
        a1 = numpy.rad2deg(roi.getStartAngle())
        a2 = numpy.rad2deg(roi.getEndAngle())
        if a2 < a1:
            # Normalize to a strict positive angle
            a1, a2 = a2, a1
        name = roi.getName()
        shape = lima_rois.ArcRoi(cx, cy, r1, r2, a1, a2, name=name)
    else:
        shape = None

    return shape
