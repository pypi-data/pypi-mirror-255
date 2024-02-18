# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
from typing import List

import numpy
import logging

from silx.gui import qt
from silx.gui.plot.items.marker import Marker
from silx.gui.plot.items.scatter import Scatter
from silx.gui.plot.items.curve import Curve
from silx.gui.plot.items.histogram import Histogram
from silx.gui.plot.items.image import ImageBase
from silx.gui.plot.items import YAxisMixIn
from silx.gui.plot.items import BoundingRect

from bliss.flint.model import plot_item_model
from .plot_helper import FlintItemMixIn
from .plot_helper import FlintPlot
from .plot_helper import MouseMovedEvent


_logger = logging.getLogger(__name__)


class TooltipItemManager:

    MAX_DISTANCE = 30
    """Max distance in pixel to grab a point with the mouse"""

    MAX_SELECTED_DISTANCE = 80
    """Max distance in pixel to grab a point with the mouse on a selected item"""

    UL = """<ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 0">"""

    def __init__(self, parent: qt.QWidget, plot: FlintPlot):
        self.__parent = parent

        self.__toolTipMarker = Marker()
        self.__toolTipMarker.setName("marker-tooltip")
        self.__toolTipMarker.setColor("pink")
        self.__toolTipMarker.setSymbol("+")
        self.__toolTipMarker.setSymbolSize(8)
        self.__toolTipMarker.setVisible(False)
        self.__filterClass = None

        self.__plot = plot

        plot.sigMouseMoved.connect(self.__onMouseMove)
        plot.sigMouseLeft.connect(self.__onMouseLeft)

    def setFilter(self, filterClass):
        self.__filterClass = filterClass

    def marker(self):
        return self.__toolTipMarker

    def __onMouseMove(self, event: MouseMovedEvent):
        mouseButton = qt.QApplication.mouseButtons()
        mode = self.__plot.getInteractiveMode()
        if mouseButton == qt.Qt.NoButton and mode["mode"] in ["zoom", "pan"]:
            self.__updateTooltip(event.xPixel, event.yPixel)
        else:
            # Avoid to display the tooltip if the user is doing stuffs
            self.__updateTooltip(None, None)

    def __onMouseLeft(self):
        self.__updateTooltip(None, None)
        qt.QToolTip.hideText()

    def __normalizePickingIndices(self, item, indices: List[int], isSelected):
        if isinstance(item, ImageBase):
            # Image is a special case cause the index is a tuple of vector y,x
            for i in range(len(indices[0])):
                yield indices[0][i], indices[1][i]
        elif isinstance(item, Histogram):
            if len(indices) == 0:
                return None, None, None
            # Drop other picked indexes
            index = indices[-1]
            yield index
        elif isinstance(item, Curve):
            # Curve picking is picking the segments
            # But we care about points
            xx = item.getXData(copy=False)
            yy = item.getYData(copy=False)
            axis = item.getYAxis()
            mouse = self.__mouse

            # Test both start and stop of the segment
            ii = set([])
            for index in indices:
                ii.add(index)
                ii.add(index + 1)
            ii.discard(len(yy))

            indexes = sorted(ii)
            results = []
            for index in indexes:
                x = xx[index]
                y = yy[index]
                pos = self.__plot.dataToPixel(x, y, axis=axis)
                if pos is None:
                    continue
                # Manhattan distance
                dist = abs(pos[0] - mouse[0]) + abs(pos[1] - mouse[1])
                if isSelected:
                    maxDist = self.MAX_SELECTED_DISTANCE
                else:
                    maxDist = self.MAX_DISTANCE

                if dist < maxDist:
                    results.append((dist, index))
            if len(results) > 0:
                results = sorted(results)
                yield results[0][1]
        elif isinstance(item, Scatter):
            for index in indices:
                yield index
                return
        else:
            assert False

    def __closest(self, curve, x, y):
        """Returns the closest point from a curve item"""
        xx = curve.getXData()
        yy = curve.getYData()
        if xx is None or len(xx) == 0:
            return None, None
        xdata, ydata = self.__plot.pixelToData(x, y)
        xcoef, ycoef = self.__plot.pixelToData(1, 1)
        if xcoef == 0:
            xcoef = 1
        if ycoef == 0:
            ycoef = 1
        xcoef, ycoef = 1 / xcoef, 1 / ycoef
        dist = ((xx - xdata) * xcoef) ** 2 + ((yy - ydata) * ycoef) ** 2
        index = numpy.nanargmin(dist)
        xdata, ydata = xx[index], yy[index]
        pos = self.__plot.dataToPixel(xdata, ydata)
        if pos is None:
            return None, None
        xdata, ydata = pos
        # Manhattan distance
        dist = abs(x - xdata) + abs(y - ydata)
        return index, dist

    def __picking(self, x, y):
        # FIXME: Hack to avoid to pass it by argument, could be done in better way
        self.__mouse = x, y

        def isFilterClass(item):
            return isinstance(item, self.__filterClass)

        if x is not None:
            if self.__filterClass is not None:
                condition = isFilterClass
            else:
                condition = None
            results = [r for r in self.__plot.pickItems(x, y, condition)]
        else:
            results = []

        selectedCurve = self.__plot.getActiveCurve()
        if len(results) == 0 and x is not None:
            # Pick on the active curve with a highter tolerence
            if selectedCurve is not None:
                index, dist = self.__closest(selectedCurve, x, y)
                if index is not None and dist < self.MAX_DISTANCE:
                    yield selectedCurve, index

        for result in results:
            item = result.getItem()
            isSelected = item is selectedCurve
            indices = result.getIndices(copy=False)
            for index in self.__normalizePickingIndices(item, indices, isSelected):
                yield item, index

    def __updateTooltip(self, x, y):
        results = self.__picking(x, y)

        textResult = []
        flintModel = self.__parent.flintModel()
        scan = self.__parent.scan()

        if self.__plot.getGraphCursor() is not None and x is not None:
            plotModel = self.__parent.plotModel()
            text = self.getCrosshairTooltip(plotModel, flintModel, scan, x, y)
            if text is not None:
                textResult.append(text)

        x, y, axis = None, None, None
        for result in results:
            item, index = result
            if isinstance(item, FlintItemMixIn):
                x, y, text = item.getFlintTooltip(index, flintModel, scan)
                if text:
                    textResult.append(text)
            else:
                continue

            if isinstance(item, (Curve, Histogram)):
                axis = item.getYAxis()
            else:
                axis = "left"

        # Hack to force redisplay of the tooltip
        # FIXME: this should not be needed
        cursorPos = qt.QCursor.pos() + qt.QPoint(10, 10)
        uniqueid = f'<meta name="foo" content="{cursorPos.x()}-{cursorPos.y()}" />'

        if textResult != []:
            text = f"<html>{self.UL}" + "".join(textResult) + f"</ul>{uniqueid}</html>"
            self.__updateToolTipMarker(x, y, axis)
        else:
            text = f"<html>No data{uniqueid}</html>"
            self.__updateToolTipMarker(None, None, None)
        qt.QToolTip.showText(cursorPos, text, self.__plot)

    def __isY2AxisDisplayed(self):
        for item in self.__plot.getItems():
            if isinstance(item, BoundingRect):
                continue
            if isinstance(item, YAxisMixIn):
                if not item.isVisible():
                    continue
                if item.getYAxis() == "right":
                    return True
        return False

    def getCrosshairTooltip(self, plotModel, flintModel, scan, px, py):
        # Get a visible item
        if plotModel is None:
            return None
        if isinstance(plotModel, plot_item_model.ImagePlot):
            # Do not display it for ImagePlot
            # It's just dump information
            return None

        selectedItem = None
        for item in plotModel.items():
            if item.isVisible():
                selectedItem = item
                break

        x, y = self.__plot.pixelToData(px, py)

        y2Name = None
        if isinstance(plotModel, plot_item_model.CurvePlot):
            xName = None
            if isinstance(selectedItem, plot_item_model.CurveItem):
                xChannel = selectedItem.xChannel()
                if xChannel is not None:
                    xName = xChannel.displayName(scan)
            if xName is None:
                xName = "X"
            yName = "Y1"
            if self.__isY2AxisDisplayed():
                _, y2 = self.__plot.pixelToData(px, py, "right")
                y2Name = "Y2"
        elif isinstance(plotModel, plot_item_model.ScatterPlot):
            xName = None
            yName = None
            if isinstance(selectedItem, plot_item_model.CurveItem):
                xChannel = selectedItem.xChannel()
                if xChannel is not None:
                    xName = xChannel.displayName(scan)
            if xName is None:
                xName = "X"
            if isinstance(selectedItem, plot_item_model.ScatterItem):
                yChannel = selectedItem.xChannel()
                if yChannel is not None:
                    yName = yChannel.displayName(scan)
            if yName is None:
                yName = "Y"
        elif isinstance(plotModel, plot_item_model.McaPlot):
            x, y = int(x), int(y)
            xName = "Channel ID"
            yName = "Count"
        elif isinstance(plotModel, plot_item_model.OneDimDataPlot):
            x, y = int(x), int(y)
            xName = "Channel ID"
            yName = "Count"
        elif isinstance(plotModel, plot_item_model.ImagePlot):
            # Round to the pixel
            x, y = int(x), int(y)
            xName = "Col/X"
            yName = "Row/Y"
        else:
            xName = "x"
            yName = "y"

        char = "✛"

        text = f"""
        <li style="white-space:pre">{char} <b>Crosshair</b></li>
        <li style="white-space:pre">     <b>{xName}:</b> {x}</li>
        <li style="white-space:pre">     <b>{yName}:</b> {y}</li>
        """
        if y2Name is not None:
            text += f"""
        <li style="white-space:pre">     <b>{y2Name}:</b> {y2}</li>
        """
        return text

    def __updateToolTipMarker(self, x, y, axis):
        if x is None:
            self.__toolTipMarker.setVisible(False)
        else:
            self.__toolTipMarker.setVisible(True)
            self.__toolTipMarker.setPosition(x, y)
            self.__toolTipMarker.setYAxis(axis)
