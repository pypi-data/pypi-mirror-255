# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides plot helper class to deal with flint proxy.
"""

import logging

from bliss.flint.client.data_plot import DataPlot


_logger = logging.getLogger(__name__)


class ScatterView(DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.viewers.custom_scatter.viewer.ScatterView"

    # Available name to identify this plot
    ALIASES = ["scatter"]

    def _init(self):
        # Make it public
        self.set_colormap = self._set_colormap

    def set_data(self, x, y, value, resetzoom=True, **kwargs):
        if x is None or y is None or value is None:
            self.clear_data()
        else:
            self.submit("setData", x, y, value, resetzoom=resetzoom, **kwargs)
