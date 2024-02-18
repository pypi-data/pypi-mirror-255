# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import logging

from silx.gui import qt
from bliss.flint.widgets.custom_plot import CustomPlot

_logger = logging.getLogger(__name__)


class GridContainer(qt.QWidget):
    def __init__(self, parent=None):
        super(GridContainer, self).__init__(parent=parent)
        layout = qt.QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.__layout = layout
        self.__customPlots = {}

    def _createHolder(
        self, label, widgetClass=qt.QWidget, closeable=False, selected=False
    ):
        widget = widgetClass(parent=self)
        return widget

    def _removeHolder(self, widget):
        widget.deleteLater()

    def createCustomPlot(
        self, plotWidget, name, plot_id, selected, closeable, parentLayoutParams
    ):
        """Create a custom plot"""
        row, col, rowSpan, columnSpan = parentLayoutParams
        if row is None:
            row = 0
        if col is None:
            col = 0
        if rowSpan is None:
            rowSpan = 1
        if columnSpan is None:
            columnSpan = 1
        customPlot = self._createHolder(
            name, widgetClass=CustomPlot, selected=selected, closeable=closeable
        )
        self.__layout.addWidget(customPlot, row, col, rowSpan, columnSpan)
        customPlot.setPlotId(plot_id)
        customPlot.setName(name)
        customPlot.setPlot(plotWidget)
        self.__customPlots[plot_id] = customPlot
        plotWidget.show()
        return customPlot

    def subPlotIds(self):
        return self.__customPlots.keys()

    def removeCustomPlot(self, plot_id):
        """Remove a custom plot by its id"""
        customPlot = self.__customPlots.pop(plot_id)
        self._removeHolder(customPlot)

    def customPlot(self, plot_id) -> CustomPlot:
        """If the plot does not exist, returns None"""
        plot = self.__customPlots.get(plot_id)
        return plot
