# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Implementation of a normalization of the data between 0..1
"""
from __future__ import annotations
from typing import Optional
from typing import NamedTuple
from typing import Dict
from typing import Any

import numpy
import logging

from ..model import scan_model
from ..model import plot_model
from ..model import plot_item_model
from ..model.plot_item_model import ComputedCurveItem

_logger = logging.getLogger(__name__)


class NormalizedZeroOneData(NamedTuple):
    xx: numpy.ndarray
    yy: numpy.ndarray
    ymin: Optional[float]
    ymax: Optional[float]

    def minmax(self, vmin, vmax):
        """Returns reduced minmax between stored and other minmax.

        The update status is True if stored ymin and ymax differ from the
        resulting minmax.
        """
        ymin = self.ymin
        ymax = self.ymax
        updated = False

        if ymin != vmin:
            if vmin is not None:
                if ymin is None or vmin < ymin:
                    updated = True
                    ymin = vmin
        if ymax != vmax:
            if vmax is not None:
                if ymax is None or vmax > ymax:
                    updated = True
                    ymax = vmax

        return ymin, ymax, updated


class NormalizedZeroOneItem(ComputedCurveItem, plot_model.IncrementalComputableMixIn):
    """This item use the scan data to process result before displaying it.

    This normalize the range of the Y data in order to transform it between 0
    and 1.
    """

    NAME = "Normalized range"
    ICON_NAME = "flint:icons/item-func"

    def __init__(self, parent=None):
        ComputedCurveItem.__init__(self, parent=parent)
        plot_model.IncrementalComputableMixIn.__init__(self)

    def name(self) -> str:
        return "Normalized range [0..1]"

    def __getstate__(self):
        state: Dict[str, Any] = {}
        state.update(plot_model.ChildItem.__getstate__(self))
        state.update(plot_item_model.CurveMixIn.__getstate__(self))
        return state

    def __setstate__(self, state):
        plot_model.ChildItem.__setstate__(self, state)
        plot_item_model.CurveMixIn.__setstate__(self, state)

    def _minmax(self, array):
        if len(array) == 0:
            vmin = None
            vmax = None
        else:
            vmin = numpy.nanmin(array)
            vmax = numpy.nanmax(array)
            if not numpy.isfinite(vmin):
                vmin = None
            if not numpy.isfinite(vmax):
                vmax = None
        return vmin, vmax

    def compute(self, scan: scan_model.Scan) -> Optional[NormalizedZeroOneData]:
        sourceItem = self.source()

        xx = sourceItem.xArray(scan)
        yy = sourceItem.yArray(scan)
        if xx is None or yy is None:
            return None

        vmin, vmax = self._minmax(yy)
        if vmin is None or vmax is None:
            yy_normalized = yy
        else:
            yy_normalized = (yy - vmin) / (vmax - vmin)
        return NormalizedZeroOneData(xx, yy_normalized, vmin, vmax)

    def incrementalCompute(
        self, previousResult: NormalizedZeroOneData, scan: scan_model.Scan
    ) -> NormalizedZeroOneData:
        """Compute a data using the previous value as basis

        The derivative function expect 5 extra points before and after the
        points it can compute.

        The last computed point have to be recomputed.

        This code is deeply coupled with the implementation of the derivative
        function.
        """
        sourceItem = self.source()
        xx = sourceItem.xArray(scan)
        yy = sourceItem.yArray(scan)
        if xx is None or yy is None:
            raise ValueError("Non empty data expected")

        nb = len(previousResult.yy)
        if nb == len(yy):
            # obviously nothing to compute
            return previousResult

        new_yy = yy[len(previousResult.yy) :]

        vmin, vmax = self._minmax(new_yy)
        vmin, vmax, updated = previousResult.minmax(vmin, vmax)
        if not updated:
            if vmin is None or vmax is None:
                yy_new_normalized = yy
            else:
                yy_new_normalized = (yy - vmin) / (vmax - vmin)
            yy_normalized = yy + yy_new_normalized
        else:
            if vmin is None or vmax is None:
                yy_normalized = yy
            else:
                yy_normalized = (yy - vmin) / (vmax - vmin)
        return NormalizedZeroOneData(xx, yy_normalized, vmin, vmax)

    def displayName(self, axisName, scan: scan_model.Scan) -> str:
        """Helper to reach the axis display name"""
        sourceItem = self.source()
        if axisName == "x":
            return sourceItem.displayName("x", scan)
        elif axisName == "y":
            return "norm(%s)" % sourceItem.displayName("y", scan)
        else:
            assert False
