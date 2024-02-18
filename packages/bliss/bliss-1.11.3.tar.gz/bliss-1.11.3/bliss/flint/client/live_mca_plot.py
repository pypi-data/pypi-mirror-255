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


class LiveMcaPlot(BasePlot):

    WIDGET = None

    ALIASES = ["mca"]
