# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations

import typing
import numpy
import logging

from silx.gui import qt
from silx.gui import plot as silx_plot
import tempfile
import os

_logger = logging.getLogger(__name__)


class _DataWidget(qt.QWidget):
    def __init__(self, parent=None):
        super(_DataWidget, self).__init__(parent=parent)
        self.__silxWidget = self._createSilxWidget(self)
        self.__dataDict = {}

        frame = qt.QFrame(self)
        frame.setFrameShape(qt.QFrame.StyledPanel)
        frame.setAutoFillBackground(True)
        layout = qt.QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.__silxWidget)
        widget = qt.QFrame(self)
        layout = qt.QVBoxLayout(widget)
        layout.addWidget(frame)
        layout.setContentsMargins(0, 1, 0, 0)

        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)

    def dataDict(self):
        return self.__dataDict

    def silxWidget(self):
        return self.__silxWidget

    def silxPlot(self):
        """Used by the interactive API.

        This have to returns a PlotWidget, that's why it could be not always
        the same as the silx widget.
        """
        return self.__silxWidget

    def _createSilxWidget(self, parent):
        raise NotImplementedError

    def __getattr__(self, name: str):
        silxWidget = self.silxWidget()
        return getattr(silxWidget, name)

    def updateStoredData(self, field, data):
        data_dict = self.dataDict()

        # Data from the network is sometime not writable
        # This make it fail silx for some use cases
        if data is None:
            return None
        if isinstance(data, numpy.ndarray):
            if not data.flags.writeable:
                data = numpy.array(data)

        data_dict[field] = data

    def removeStoredData(self, field):
        data_dict = self.dataDict()
        del data_dict[field]

    def getStoredData(self, field=None):
        data_dict = self.dataDict()
        if field is None:
            return data_dict
        else:
            return data_dict.get(field, [])

    def clearStoredData(self):
        data_dict = self.dataDict()
        data_dict.clear()

    def clear(self):
        self.clearStoredData()
        self.silxWidget().clear()

    def selectStoredData(self, *names, **kwargs):
        # FIXME: This have to be moved per plot widget
        # FIXME: METHOD have to be removed
        method = self.METHOD
        if "legend" not in kwargs and method.startswith("add"):
            kwargs["legend"] = " -> ".join(names)
        data_dict = self.dataDict()
        args = tuple(data_dict[name] for name in names)
        widget_method = getattr(self, method)
        # Plot
        widget_method(*args, **kwargs)

    def deselectStoredData(self, *names):
        legend = " -> ".join(names)
        self.remove(legend)

    def exportToLogbook(self, icatClient):
        plot = self.silxPlot()
        try:
            f = tempfile.NamedTemporaryFile(delete=False)
            filename = f.name
            f.close()
            os.unlink(filename)
            plot.saveGraph(filename, fileFormat="png")
            with open(filename, "rb") as f:
                data = f.read()
            os.unlink(filename)
        except Exception:
            _logger.error("Error while creating the screenshot", exc_info=True)
            raise Exception("Error while creating the screenshot")
        try:
            icatClient.send_binary_data(data=data, mimetype="image/png")
        except Exception:
            _logger.error("Error while sending the screenshot", exc_info=True)
            raise Exception("Error while sending the screenshot")


class Plot1D(_DataWidget):
    """Generic plot to display 1D data"""

    # Name of the method to add data to the plot
    METHOD = "addCurve"

    class CurveItem(typing.NamedTuple):
        xdata: str
        ydata: str
        style: typing.Dict[str, object]

    def __init__(self, parent=None):
        _DataWidget.__init__(self, parent=parent)
        self.__items = {}
        self.__autoUpdatePlot = True
        self.__raiseOnException = False

    def setRaiseOnException(self, raises):
        """To simplify remote debug"""
        self.__raiseOnException = raises

    def _createSilxWidget(self, parent):
        widget = silx_plot.Plot1D(parent=parent)
        widget.setDataMargins(0.05, 0.05, 0.05, 0.05)
        widget.setActiveCurveStyle(linewidth=2, symbol=".")
        return widget

    def setAutoUpdatePlot(self, update="bool"):
        """Set to true to enable or disable update of plot for each changes of
        the data or items"""
        self.__autoUpdatePlot = update

    def clearItems(self):
        """Remove the item definitions"""
        self.__items.clear()
        self.__updatePlotIfNeeded()

    def removeItem(self, legend: str):
        """Remove a specific item by name"""
        del self.__items[legend]
        self.__updatePlotIfNeeded()

    def getItem(self, legend: str):
        item = self.__items[legend]
        return item._asdict()

    def itemExists(self, legend: str):
        """True if a specific item exists."""
        return legend in self.__items

    def addCurveItem(
        self, xdata: str, ydata: str, legend: str = None, color=None, **kwargs
    ):
        """Define an item which have to be displayed with the specified data
        name
        """
        if legend is None:
            legend = ydata + " -> " + xdata
        if color is not None:
            if isinstance(color, str):
                if color.startswith("color"):
                    # FIXME: This could be removed in the future: silx > 1.1 will implement it
                    icolor = int(color[5:])
                    colorList = self.silxWidget().colorList
                    color = colorList[icolor % len(colorList)]
            kwargs["color"] = color
        self.__items[legend] = self.CurveItem(xdata, ydata, kwargs)
        self.__updatePlotIfNeeded()

    def setData(self, **kwargs):
        dataDict = self.dataDict()
        for k, v in kwargs.items():
            dataDict[k] = v
        self.__updatePlotIfNeeded()

    def appendData(self, **kwargs):
        dataDict = self.dataDict()
        for k, v in kwargs.items():
            d = dataDict.get(k, None)
            if d is None:
                d = v
            else:
                d = numpy.concatenate((d, v))
            dataDict[k] = d
        self.__updatePlotIfNeeded()

    def clear(self):
        super(Plot1D, self).clear()
        self.__updatePlotIfNeeded()

    def updatePlot(self, resetzoom: bool = True):
        try:
            self.__updatePlot()
        except Exception:
            _logger.error("Error while updating the plot", exc_info=True)
            if self.__raiseOnException:
                raise
        if resetzoom:
            self.resetZoom()

    def __updatePlotIfNeeded(self):
        if self.__autoUpdatePlot:
            self.updatePlot(resetzoom=True)

    def __updatePlot(self):
        plot = self.silxPlot()
        unusedCurves = set([c.getLegend() for c in plot.getAllCurves()])

        dataDict = self.dataDict()
        for legend, item in self.__items.items():
            unusedCurves.discard(legend)
            xData = dataDict.get(item.xdata)
            yData = dataDict.get(item.ydata)
            if xData is None or yData is None:
                continue
            if len(yData) != len(xData):
                size = min(len(yData), len(xData))
                xData = xData[0:size]
                yData = yData[0:size]
            if len(yData) == 0:
                continue

            style = {**item.style}
            prevItem = plot.getCurve(legend)
            if prevItem is not None:
                # Sounds like it is mandatory for silx 2.0
                # replace=True does not work with default style
                plot.removeCurve(legend)
                if "color" not in style:
                    # Restore the previous color
                    style["color"] = prevItem.getColor()

            plot.addCurve(xData, yData, legend=legend, **style, resetzoom=False)

        for legend in unusedCurves:
            plot.removeCurve(legend)

    def getXAxisScale(self):
        plot = self.silxPlot()
        return "log" if plot.isXAxisLogarithmic() else "linear"

    def setXAxisScale(self, scale):
        assert scale in ["log", "linear"]
        plot = self.silxPlot()
        plot.setXAxisLogarithmic(scale == "log")

    def getYAxisScale(self):
        plot = self.silxPlot()
        return "log" if plot.isYAxisLogarithmic() else "linear"

    def setYAxisScale(self, scale):
        assert scale in ["log", "linear"]
        plot = self.silxPlot()
        plot.setYAxisLogarithmic(scale == "log")


class Plot2D(_DataWidget):
    """Generic plot to display 2D data"""

    # Name of the method to add data to the plot
    METHOD = "addImage"

    def _createSilxWidget(self, parent):
        widget = silx_plot.Plot2D(parent=parent)
        widget.setDataMargins(0.05, 0.05, 0.05, 0.05)
        return widget

    def getYaxisDirection(self) -> str:
        """Returns the direction of the y-axis.

        Returns:
            One of "up", "down"
        """
        inverted = self.silxWidget().getYAxis().isInverted()
        return "down" if inverted else "up"

    def setYaxisDirection(self, direction: str):
        """Specify the direction of the y-axis.

        By default the direction is up, which mean the 0 is on bottom, and
        positive values are above.

        Argument:
            direction: One of "up", "down"
        """
        assert direction in ("up", "down")
        inverted = direction == "down"
        self.silxWidget().getYAxis().setInverted(inverted)

    def setDisplayedIntensityHistogram(self, show):
        self.getIntensityHistogramAction().setVisible(show)


class ImageTooltip:

    UL = """<ul style="margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 0">"""

    def _formatValueToString(self, value):
        try:
            if isinstance(value, numpy.ndarray):
                if len(value) == 4:
                    return "<b>RGBA</b>: %.3g, %.3g, %.3g, %.3g" % (
                        value[0],
                        value[1],
                        value[2],
                        value[3],
                    )
                elif len(value) == 3:
                    return "<b>RGB</b>: %.3g, %.3g, %.3g" % (
                        value[0],
                        value[1],
                        value[2],
                    )
            else:
                return "<b>Value</b>: %g" % value
        except Exception:
            _logger.error("Error while formatting pixel value", exc_info=True)
        return "<b>Value</b>: %s" % value

    def hide(self):
        qt.QToolTip.hideText()

    def showUnderMouse(self, widget, row, column, value):
        msg = ""
        if numpy.isnan(column) or numpy.isnan(row):
            # Triggered with mouse over the side histograms
            if not numpy.isnan(column):
                msg += f"<li><b>Column/x</b>: {int(column)}</li>"
                msg += f"<li><b>Sum</b>: {value:g}</li>"
            if not numpy.isnan(row):
                msg += f"<li><b>Row/y</b>: {int(row)}</li>"
                msg += f"<li><b>Sum</b>: {value:g}</li>"
        else:
            # FIXME: col and row looks swapped
            msg += f"<li><b>Index (row/col)</b>: {int(column)}, {int(row)}</li>"
            msg_value = self._formatValueToString(value)
            msg += f"<li>{msg_value}</li>"

        cursorPos = qt.QCursor.pos() + qt.QPoint(10, 10)
        uniqueid = f'<meta name="foo" content="{cursorPos.x()}-{cursorPos.y()}" />'

        if msg != "":
            text = f"<html>{self.UL}{msg}</ul>{uniqueid}</html>"
        else:
            text = f"<html>No data{uniqueid}</html>"
        qt.QToolTip.showText(cursorPos, text, widget)


class ImageView(_DataWidget):
    """Dedicated plot to display an image"""

    # Name of the method to add data to the plot
    METHOD = "setImage"

    class _PatchedImageView(silx_plot.ImageView):
        def isSideHistogramDisplayed(self):
            """True if the side histograms are displayed"""
            # FIXME: This have to be fixed in silx <= 1.1
            return self._histoHPlot.isVisibleTo(self)

    def _createSilxWidget(self, parent):
        widget = self._PatchedImageView(parent=parent)
        widget.setDataMargins(0.05, 0.05, 0.05, 0.05)
        widget.valueChanged.connect(self._updateTooltip)
        self._tooltip = ImageTooltip()
        return widget

    def getYaxisDirection(self) -> str:
        """Returns the direction of the y-axis.

        Returns:
            One of "up", "down"
        """
        inverted = self.silxWidget().getYAxis().isInverted()
        return "down" if inverted else "up"

    def setYaxisDirection(self, direction: str):
        """Specify the direction of the y-axis.

        By default the direction is up, which mean the 0 is on bottom, and
        positive values are above.

        Argument:
            direction: One of "up", "down"
        """
        assert direction in ("up", "down")
        inverted = direction == "down"
        self.silxWidget().getYAxis().setInverted(inverted)

    def setDisplayedIntensityHistogram(self, show):
        self.getIntensityHistogramAction().setVisible(show)

    def _updateTooltip(self, row, column, value):
        """Update status bar with coordinates/value from plots."""
        widget = self.silxPlot()
        self._tooltip.showUnderMouse(widget, row, column, value)


class ScatterView(_DataWidget):
    """Dedicated plot to display a 2D scatter"""

    # Name of the method to add data to the plot
    METHOD = "setData"

    def _createSilxWidget(self, parent):
        widget = silx_plot.ScatterView(parent=parent)
        plot = widget.getPlotWidget()
        plot.setDataMargins(0.05, 0.05, 0.05, 0.05)
        return widget

    def getDataRange(self):
        plot = self.silxWidget().getPlotWidget()
        return plot.getDataRange()

    def clear(self):
        self.silxWidget().setData(None, None, None)

    def setData(
        self, x, y, value, xerror=None, yerror=None, alpha=None, resetzoom=True
    ):
        self.silxWidget().setData(
            x, y, value, xerror=xerror, yerror=yerror, alpha=alpha, copy=False
        )
        if resetzoom:
            # Else the view is not updated
            self.resetZoom()


class ScatterView3D(_DataWidget):
    """Dedicated plot to display a 3D scatter"""

    # Name of the method to add data to the plot
    METHOD = "setData"

    def _createSilxWidget(self, parent):
        from silx.gui.plot3d.SceneWindow import SceneWindow
        from silx.gui.plot3d import items

        widget = SceneWindow(parent=parent)
        sceneWidget = widget.getSceneWidget()
        item = items.Scatter3D()
        item.setSymbol(",")
        sceneWidget.addItem(item)

        # FIXME: that's small hack to store the item
        widget._item = item
        widget._first_render = True
        return widget

    def silxItem(self):
        widget = self.silxPlot()
        return widget._item

    def getDataRange(self):
        widget = self.silxPlot()
        sceneWidget = widget.getSceneWidget()
        bounds = sceneWidget.viewport.scene.bounds(transformed=True)
        return bounds

    def clear(self):
        item = self.silxItem()
        item.setData([numpy.nan], [numpy.nan], [numpy.nan], [numpy.nan])

    def setMarker(self, symbol):
        item = self.silxItem()
        item.setSymbol(symbol)

    def getColormap(self):
        item = self.silxItem()
        return item.getColormap()

    def setData(self, x, y, z, value):
        item = self.silxItem()
        item.setData(x, y, z, value, copy=False)
        widget = self.silxPlot()
        if widget._first_render:
            widget._first_render = False
            widget.getSceneWidget().resetZoom()


class Plot3D(_DataWidget):
    """Dedicated plot to display a 3D scatter"""

    # Name of the method to add data to the plot
    METHOD = "setData"

    class ScatterItem(typing.NamedTuple):
        xdata: str
        ydata: str
        zdata: str
        vdata: str

        @property
        def channelNames(self):
            return {self.xdata, self.ydata, self.zdata, self.vdata}

    class MeshItem(typing.NamedTuple):
        vertices: str
        faces: str
        color: numpy.ndarray

        @property
        def channelNames(self):
            return {self.vertices, self.faces}

    def __init__(self, parent=None):
        _DataWidget.__init__(self, parent=parent)
        self.__items = {}
        self.__plotItems = {}
        self.__autoUpdatePlot = True
        self.__raiseOnException = False
        self.__firstRendering = True

    def setAutoUpdatePlot(self, update="bool"):
        """Set to true to enable or disable update of plot for each changes of
        the data or items"""
        self.__autoUpdatePlot = update

    def addScatterItem(
        self,
        xdata: str,
        ydata: str,
        zdata: str,
        vdata: str,
        legend: str = None,
        symbol: str = ",",
        symbolSize: float = None,
        lut=None,
        vmin=None,
        vmax=None,
    ):
        """Define an item which have to be displayed with the specified data
        name
        """
        if legend is None:
            legend = f"{xdata},{ydata},{zdata} -> {vdata}"
        self.__items[legend] = self.ScatterItem(xdata, ydata, zdata, vdata)

        widget = self.silxPlot()
        sceneWidget = widget.getSceneWidget()
        if legend in self.__plotItems:
            i = self.__plotItems[legend]
            sceneWidget.removeItem(i)

        from silx.gui.plot3d import items

        item = items.Scatter3D()
        item.setSymbol(symbol)
        item.setSymbolSize(symbolSize)
        colormap = item.getColormap()
        if lut is not None:
            colormap.setName(lut)
        if vmin is not None:
            colormap.setVMin(vmin)
        if vmax is not None:
            colormap.setVMax(vmax)
        sceneWidget.addItem(item)
        self.__plotItems[legend] = item
        self.__updatePlotIfNeeded()

    def addMeshItem(
        self,
        vertices: str,
        faces: str,
        legend: str = None,
        color=None,
    ):
        """Define an item which have to be displayed with the specified data
        name
        """
        if legend is None:
            legend = f"{vertices} x {faces}"
        self.__items[legend] = self.MeshItem(vertices, faces, color)

        widget = self.silxPlot()
        sceneWidget = widget.getSceneWidget()
        if legend in self.__plotItems:
            i = self.__plotItems[legend]
            sceneWidget.removeItem(i)

        from silx.gui.plot3d import items

        item = items.Mesh()
        sceneWidget.addItem(item)
        self.__plotItems[legend] = item
        self.__updatePlotIfNeeded()

    def clearItems(self):
        for name in self.__plotItems.keys():
            self.removeItem(name)

    def removeItem(self, legend: str):
        """Remove a specific item by name"""
        i = self.__plotItems.pop(legend)
        widget = self.silxPlot()
        sceneWidget = widget.getSceneWidget()
        sceneWidget.removeItem(i)

    def _createSilxWidget(self, parent):
        from silx.gui.plot3d.SceneWindow import SceneWindow

        widget = SceneWindow(parent=parent)
        return widget

    def getDataRange(self):
        widget = self.silxPlot()
        sceneWidget = widget.getSceneWidget()
        bounds = sceneWidget.viewport.scene.bounds(transformed=True)
        return bounds

    def clear(self):
        super(Plot3D, self).clear()
        self.__updatePlot()

    def setData(self, **kwargs):
        dataDict = self.dataDict()
        for k, v in kwargs.items():
            dataDict[k] = v
        self.__updatePlotIfNeeded(updatedChannels=kwargs.keys())

    def resetZoom(self):
        widget = self.silxPlot()
        sceneWidget = widget.getSceneWidget()
        sceneWidget.resetZoom()

    def __updatePlotIfNeeded(self, updatedChannels=None):
        if self.__autoUpdatePlot:
            self.updatePlot(resetzoom=False, updatedChannels=updatedChannels)

    def updatePlot(self, resetzoom: bool = True, updatedChannels=None):
        try:
            self.__updatePlot(updatedChannels=updatedChannels)
        except Exception:
            _logger.error("Error while updating the plot", exc_info=True)
            if self.__raiseOnException:
                raise
        if resetzoom or self.__firstRendering:
            self.__firstRendering = False
            self.resetZoom()

    def __iterItemsUsingChannels(self, channelNames):
        channelNames = set(channelNames)
        for legend, item in self.__items.items():
            if len(item.channelNames.intersection(channelNames)) != 0:
                yield legend, item

    def __getClampedData(self, *args):
        dataDict = self.dataDict()
        data = [dataDict.get(n) for n in args]
        if True in [d is None for d in data]:
            return [None] * len(args)
        smallest = min([len(d) for d in data])
        data = [d[0:smallest] for d in data]
        return data

    def __getData(self, *args):
        dataDict = self.dataDict()
        data = [dataDict.get(n) for n in args]
        if True in [d is None for d in data]:
            return [None] * len(args)
        return data

    def __updatePlot(self, updatedChannels=None):
        if updatedChannels is None:
            updatedItems = self.__items.items()
        else:
            updatedItems = self.__iterItemsUsingChannels(updatedChannels)

        for legend, item in updatedItems:
            try:
                if isinstance(item, self.ScatterItem):
                    xData, yData, zData, vData = self.__getClampedData(
                        item.xdata, item.ydata, item.zdata, item.vdata
                    )
                    if xData is None:
                        continue
                    pitem = self.__plotItems[legend]
                    pitem.setData(xData, yData, zData, vData, copy=False)
                elif isinstance(item, self.MeshItem):
                    vertices, faces = self.__getData(item.vertices, item.faces)
                    if vertices is None:
                        continue
                    pitem = self.__plotItems[legend]
                    faces = numpy.array(faces)
                    if faces.dtype.kind != "u":
                        faces = numpy.array(faces, dtype=numpy.uint32)
                    pitem.setData(position=vertices, indices=faces, color=item.color)
            except Exception:
                _logger.error("Error while updating the item %s", legend, exc_info=True)


class StackImageView(_DataWidget):
    """Dedicated plot to display a stack of images"""

    # Name of the method to add data to the plot
    METHOD = "setStack"

    def _createSilxWidget(self, parent):
        stack = silx_plot.StackView(parent=parent)
        stack.valueChanged.connect(self._updateTooltip)
        self._tooltip = ImageTooltip()
        return stack

    def _updateTooltip(self, row, column, value):
        """Update status bar with coordinates/value from plots."""
        widget = self.silxPlot()
        if value is None:
            self._tooltip.hide()
        else:
            self._tooltip.showUnderMouse(widget, row, column, value)

    def getDataRange(self):
        plot = self.silxWidget().getPlotWidget()
        return plot.getDataRange()
