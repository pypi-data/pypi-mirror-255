# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides plot helper class to deal with flint proxy.
"""

from typing import Optional
from typing import Tuple

import logging
import numpy

from .base_plot import BasePlot

_logger = logging.getLogger(__name__)


class _LiveImageProcessing:
    def __init__(self, proxy):
        self.__proxy = proxy

    def _submit(self, cmd, *args, **kwargs):
        self.__proxy.submit(cmd, *args, **kwargs)

    def set_flat(self, array, expotime):
        """Specify a flat which will be used for the flatfield correction."""
        array = numpy.asarray(array)
        self._submit(
            "imageProcessing().flatFieldStage().setFlat", array, exposureTime=expotime
        )

    def set_dark(self, array, expotime):
        """Specify a dark which will be used for the flatfield correction."""
        array = numpy.asarray(array)
        self._submit(
            "imageProcessing().flatFieldStage().setDark", array, exposureTime=expotime
        )

    def set_mask(self, array):
        """Specify a mask which will be used to mask pixels."""
        array = numpy.asarray(array)
        self._submit("imageProcessing().maskStage().setMask", array)


class LiveImagePlot(BasePlot):

    WIDGET = None

    ALIASES = ["image"]

    def _init(self):
        # Make it public
        self.set_colormap = self._set_colormap
        self.__processing = None

    def update_marker(
        self,
        unique_name: str,
        position: Optional[Tuple[float, float]] = None,
        text: Optional[str] = None,
        editable: Optional[bool] = None,
        kind: Optional[str] = None,
    ):
        """
        Create or update a marker into the image.

        Arguments:
            unique_name: Unique name identifying this marker
            position: X and Y position in the image, else None to remove the marker
            text: Text to display with the marker
            editable: If true, the marker can be moved with the mouse
            kind: Shape of the ROI. One of `point`, `cross`, `vline`, `hline`
        """
        self.submit(
            "updateMarker",
            uniqueName=unique_name,
            position=position,
            text=text,
            editable=editable,
            kind=kind,
        )

    def remove_marker(self, unique_name: str):
        """
        Remove a marker already existing.

        If the marker is not there, no feedback is returned.

        Arguments:
            unique_name: Unique name identifying this marker
        """
        self.submit("removeMarker", uniqueName=unique_name)

    def marker_position(self, unique_name: str) -> Optional[Tuple[float, float]]:
        """
        Create or update a marker into the image.

        Arguments:
            unique_name: Unique name identifying this marker

        Returns:
            The position of the marker, else None if the marker does not exist
        """
        p = self.submit("markerPosition", uniqueName=unique_name)
        if p is None:
            return None
        # FIXME: the RPC returns a list instead of a tuple
        return tuple(p)

    @property
    def processing(self):
        if self.__processing is None:
            self.__processing = _LiveImageProcessing(self)
        return self.__processing
