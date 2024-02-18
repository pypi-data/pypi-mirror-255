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

import numpy
import logging

from .base_plot import BasePlot

_logger = logging.getLogger(__name__)


class LiveCurvePlot(BasePlot):

    WIDGET = None

    ALIASES = ["curve"]

    def update_user_data(
        self, unique_name: str, channel_name: str, ydata: Optional[numpy.ndarray]
    ):
        """Add user data to a live plot.

        It will define a curve in the plot using the y-data provided and the
        x-data from the parent item (defined by the `channel_name`)

        The key `unique_name` + `channel_name` is unique. So if it already
        exists the item will be updated.

        Arguments:
            unique_name: Name of this item in the property tree
            channel_name: Name of the channel that will be used as parent for
                this item. If this parent item does not exist, it is created
                but set hidden.
            ydata: Y-data for this item. If `None`, if the item already exists,
                it is removed from the plot
        """
        if ydata is not None:
            ydata = numpy.asarray(ydata)
        self._flint.update_user_data(self._plot_id, unique_name, channel_name, ydata)

    def update_axis_marker(
        self, unique_name: str, channel_name, position: float, text: str
    ):
        """
        Display a vertical marker for a specific x-axis channel name.

        Arguments:
            unique_name: Unique name identifying this marker
            channel_name: X-axis name in which the marker have to be displayed (for example `axis:foo`)
                          The marker will only be displayed if the actual plot's x-axis is this channel
            position: Position of this marker in the `channel_name` axis
            text: Text to display with the marker
        """
        self._flint.update_axis_marker(
            self._plot_id, unique_name, channel_name, position, text
        )

    @property
    def xscale(self):
        """
        Scale of the x-axis of this plot.

        The value is one of "linear", "log"
        """
        return self.submit("getXAxisScale")

    @xscale.setter
    def xscale(self, scale):
        self.submit("setXAxisScale", scale)

    @property
    def yscale(self):
        """
        Scale of the y-axis of this plot.

        The value is one of "linear", "log"
        """
        return self.submit("getYAxisScale")

    @yscale.setter
    def yscale(self, scale):
        self.submit("setYAxisScale", scale)

    @property
    def xaxis_channel_name(self):
        """Returns the channel name used as x-axis, else None"""
        return self.submit("getXAxisChannelName")
