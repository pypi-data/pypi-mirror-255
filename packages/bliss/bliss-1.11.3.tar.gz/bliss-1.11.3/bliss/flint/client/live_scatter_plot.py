# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides plot interface exposed inside BLISS shell.
"""

import logging

from .base_plot import BasePlot

_logger = logging.getLogger(__name__)


class LiveScatterPlot(BasePlot):

    WIDGET = None

    ALIASES = ["scatter"]

    def _init(self):
        # Make it public
        self.set_colormap = self._set_colormap

    @property
    def xaxis_channel_name(self):
        """Returns the channel name used as x-axis, else None"""
        return self.submit("getXAxisChannelName")

    @property
    def yaxis_channel_name(self):
        """Returns the channel name used as y-axis, else None"""
        return self.submit("getYAxisChannelName")
