# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

from __future__ import annotations
from typing import Optional
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Tuple

import logging
import numpy
import weakref

from silx.gui import qt
from silx.gui import utils
from silx.gui import icons
from silx.gui import colors
from silx.gui.plot.actions import histogram
from silx.gui.plot.items.marker import Marker
from silx.gui.plot.tools.RadarView import RadarView
from silx.gui.plot.tools.roi import RegionOfInterestManager
from silx.gui.plot.utils.axis import SyncAxes
from silx.gui.plot.items import roi as roi_items

from bliss.flint.model import scan_model
from bliss.flint.model import flint_model
from bliss.flint.model import plot_model
from bliss.flint.model import style_model
from bliss.flint.model import plot_item_model
from bliss.flint.helper import scan_info_helper
from bliss.flint.helper import model_helper
from bliss.flint.widgets.utils import roi_helper
from .utils import plot_helper
from .utils import image_helper
from .utils import view_helper
from .utils import refresh_helper
from .utils import tooltip_helper
from .utils import export_action
from .utils import marker_action
from .utils import camera_live_action
from .utils import profile_action
from .utils import plot_action
from .utils import style_action
from .image_stages.info import ImageLayer
from .image_stages.info import ImageCorrections
from .image_stages.mask_stage import MaskStage
from .image_stages.flat_field_stage import FlatFieldStage
from .image_stages.flat_field_stage import extract_exposure_time
from .image_stages.exposure_time_stage import ExposureTimeStage
from .image_stages.iso_contour_stage import IsoContourStage
from .image_stages.saturation_stage import SaturationStage
from .image_stages.statistics_stage import StatisticsStage


_logger = logging.getLogger(__name__)


class _ItemDescription(NamedTuple):
    key: str
    kind: str
    shape: numpy.ndarray


class _Title:
    def __init__(self, plot):
        self.__plot = plot

        self.__hasPreviousImage: bool = False
        """Remember that there was an image before this scan, to avoid to
        override the title at startup and waiting for the first image"""
        self.__lastSubTitle = None
        """Remembers the last subtitle in case it have to be reuse when
        displaying the data from the previous scan"""
        self.__kind = None
        self.__corrections = None

    def itemUpdated(self, scan, item, kind, corrections):
        self.__kind = kind
        self.__corrections = corrections
        self.__updateAll(scan, item)

    def scanRemoved(self, scan):
        """Removed scan, just before using another scan"""
        if scan is not None:
            self.__updateTitle("From previous scan")
            self.__hasPreviousImage = True
        else:
            self.__hasPreviousImage = False

    def scanStarted(self, scan):
        self.__kind = None
        self.__corrections = None
        if not self.__hasPreviousImage:
            self.__updateAll(scan)

    def scanFinished(self, scan):
        title = scan_info_helper.get_full_title(scan)
        if scan.state() == scan_model.ScanState.FINISHED:
            title += " (finished)"
        self.__updateTitle(title)

    def __formatItemTitle(self, scan: scan_model.Scan, item=None):
        if item is None:
            return None
        channel = item.imageChannel()
        if channel is None:
            return None

        frameInfo = ""
        if self.__kind == ImageLayer.DARK:
            displayName = "dark"
        elif self.__kind == ImageLayer.FLAT:
            displayName = "flat"
        else:
            displayName = channel.displayName(scan)
        shape = ""
        data = channel.data(scan)
        if data is not None:
            array = data.array()
            if array is not None:
                height, width = array.shape[0:2]
                shape = f": {width} × {height}"

            if data.source() == "video":
                op = " ≈ "
            else:
                op = " = "

            if data.frameId() is not None:
                frameInfo = f", id{op}{data.frameId()}"
            if frameInfo != "":
                frameInfo += " "
            frameInfo += f"[{data.source()}]"
        correction = ""
        if self.__corrections:
            corrections = " + ".join([str(c.value) for c in self.__corrections])
            suffix = "correction" if len(self.__corrections) == 1 else "corrections"
            correction = f", {corrections} {suffix}"
        return f"{displayName}{shape}{frameInfo}{correction}"

    def __updateTitle(self, title):
        subtitle = None
        if self.__lastSubTitle is not None:
            subtitle = self.__lastSubTitle
        if subtitle is not None:
            title = f"{title}\n{subtitle}"
        self.__plot.setGraphTitle(title)

    def __updateAll(self, scan: scan_model.Scan, item=None):
        title = scan_info_helper.get_full_title(scan)
        subtitle = None
        itemTitle = self.__formatItemTitle(scan, item)
        self.__lastSubTitle = itemTitle
        if itemTitle is not None:
            subtitle = f"{itemTitle}"
        if subtitle is not None:
            title = f"{title}\n{subtitle}"

        self.__plot.setGraphTitle(title)


class FilterAction(qt.QWidgetAction):
    """Action providing few filters to the image"""

    def __init__(self, parent):
        qt.QWidgetAction.__init__(self, parent)
        maskStage = parent.imageProcessing().maskStage()

        toolButton = qt.QToolButton(parent)

        filterAction = qt.QAction(self)
        filterAction.setText("No filter")
        filterAction.setCheckable(True)
        filterAction.setChecked(True)
        densityNoFilterAction = filterAction

        filterAction = qt.QAction(self)
        filterAction.setText("Max filter")
        filterAction.setCheckable(True)
        filterAction.setProperty(
            "aggregation-mode", plot_helper.FlintImageDensityMap.Aggregation.MAX
        )
        densityMaxFilterAction = filterAction

        filterAction = qt.QAction(self)
        filterAction.setText("Mean filter")
        filterAction.setCheckable(True)
        filterAction.setProperty(
            "aggregation-mode", plot_helper.FlintImageDensityMap.Aggregation.MEAN
        )
        densityMeanFilterAction = filterAction

        filterAction = qt.QAction(self)
        filterAction.setText("Min filter")
        filterAction.setCheckable(True)
        filterAction.setProperty(
            "aggregation-mode", plot_helper.FlintImageDensityMap.Aggregation.MIN
        )
        densityMinFilterAction = filterAction

        densityGroup = qt.QActionGroup(self)
        densityGroup.setExclusive(True)
        densityGroup.addAction(densityNoFilterAction)
        densityGroup.addAction(densityMaxFilterAction)
        densityGroup.addAction(densityMeanFilterAction)
        densityGroup.addAction(densityMinFilterAction)
        densityGroup.triggered.connect(parent.updateAll)
        self.__densityGroup = densityGroup

        maskLoadedAction = qt.QAction(self)
        maskLoadedAction.setEnabled(False)
        loadMaskAction = qt.QAction(self)
        loadMaskAction.setText("Load a mask file...")
        loadMaskAction.triggered.connect(maskStage.requestMaskFile)
        removeMaskAction = qt.QAction(self)
        removeMaskAction.setText("Remove the mask")
        removeMaskAction.triggered.connect(self.__removeMask)
        self.__maskLoadedAction = maskLoadedAction
        self.__removeMaskAction = removeMaskAction
        self.__loadMaskAction = loadMaskAction

        displayMaskAction = qt.QAction(self)
        displayMaskAction.setText("Display the mask")
        displayMaskAction.setCheckable(True)
        displayMaskAction.setChecked(True)
        displayMaskAction.toggled.connect(maskStage.setMaskDisplayedAsLayer)

        self.__displayMaskAction = displayMaskAction

        filterMenu = qt.QMenu(toolButton)
        filterMenu.aboutToShow.connect(self.__menuAboutToShow)
        filterMenu.addSection("Dynamic density filter")
        filterMenu.addAction(densityNoFilterAction)
        filterMenu.addAction(densityMaxFilterAction)
        filterMenu.addAction(densityMeanFilterAction)
        filterMenu.addAction(densityMinFilterAction)
        filterMenu.addSection("Mask")
        filterMenu.addAction(maskLoadedAction)
        filterMenu.addAction(displayMaskAction)
        filterMenu.addAction(loadMaskAction)
        filterMenu.addAction(removeMaskAction)

        toolButton.setPopupMode(qt.QToolButton.InstantPopup)
        toolButton.setMenu(filterMenu)
        toolButton.setText("Data filters")
        toolButton.setToolTip("Enable/disable filter on the image")
        icon = icons.getQIcon("flint:icons/data-filter")
        toolButton.setIcon(icon)

        self.setDefaultWidget(toolButton)

    def __removeMask(self):
        parent = self.parent()
        parent.imageProcessing().maskStage().setMask(None)

    def __menuAboutToShow(self):
        parent = self.parent()
        maskStage = parent.imageProcessing().maskStage()
        if maskStage.mask() is not None:
            self.__maskLoadedAction.setText("A mask is loaded")
            self.__removeMaskAction.setVisible(True)
            self.__displayMaskAction.setVisible(True)
        else:
            self.__maskLoadedAction.setText("No mask loaded")
            self.__removeMaskAction.setVisible(False)
            self.__displayMaskAction.setVisible(False)
        self.__displayMaskAction.setChecked(maskStage.isMaskDisplayedAsLayer())

    def setDensityMethod(self, method):
        for a in self.__densityGroup.actions():
            if a.property("aggregation-mode") is method:
                a.setChecked(True)

    def densityMethod(self):
        """Returns numpy method used for density reduction"""
        densityAction = self.__densityGroup.checkedAction()
        if densityAction is None:
            return None
        return densityAction.property("aggregation-mode")


class ImagePlotWidgetApi:
    def __init__(self, parent):
        self._parent: ImagePlotWidget = parent
        self._markers = weakref.WeakValueDictionary()

    def updateMarker(
        self,
        uniqueName: str,
        position: Optional[Tuple[float, float]] = None,
        text: Optional[str] = None,
        editable: Optional[bool] = None,
        kind: Optional[str] = None,
    ):
        """
        Create or update a marker into the image.

        Arguments:
            uniqueName: Unique name identifying this marker
            position: X and Y position in the image, else None to remove the marker
            text: Text to display with the marker
            editable: If true, the marker can be moved with the mouse
            kind: Shape of the ROI. One of `point`, `cross`, `vline`, `hline`
        """
        item = self._markers.get(uniqueName, None)
        manager = self._parent.markerAction().getRoiManager()
        wasNotThere = item is None
        if item is None:
            if kind in (None, "point", "."):
                item = roi_items.PointROI(manager)
            elif kind in ("cross", "+"):
                item = roi_items.CrossROI(manager)
            elif kind in ("vline", "|"):
                item = roi_items.VerticalLineROI(manager)
            elif kind in ("hline", "-"):
                item = roi_items.HorizontalLineROI(manager)
            else:
                raise ValueError(f"Expected one of '.-+|', found {kind}")

        if position is not None:
            item.setPosition(position)
        if editable is not None:
            item.setEditable(editable)
        if text is not None:
            item.setName(text)

        if wasNotThere:
            manager.addRoi(item)
            self._markers[uniqueName] = item

    def removeMarker(self, uniqueName: str):
        """
        Remove a marker already existing.

        If the marker is not there, no feedback is returned.

        Arguments:
            uniqueName: Unique name identifying this marker
        """
        item = self._markers.pop(uniqueName, None)
        manager = self._parent.markerAction().getRoiManager()
        if item is not None:
            manager.removeRoi(item)
            item.deleteLater()

    def markerPosition(self, uniqueName: str) -> Optional[Tuple[float, float]]:
        """
        Create or update a marker into the image.

        Arguments:
            unique_name: Unique name identifying this marker

        Returns:
            The position of the marker, else None if the marker does not exist
        """
        item = self._markers.get(uniqueName, None)
        if item is None:
            return None
        return item.getPosition()


class _ImageProcessing(qt.QObject):
    """Handle the processing applied on the image"""

    configUpdated = qt.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__maskStage = MaskStage(self)
        self.__maskStage.configUpdated.connect(self.__configUpdated)
        self.__flatFieldStage = FlatFieldStage(self)
        self.__flatFieldStage.configUpdated.connect(self.__configUpdated)
        self.__exposureTimeStage = ExposureTimeStage(self)
        self.__exposureTimeStage.configUpdated.connect(self.__configUpdated)
        self.__saturationStage = SaturationStage(self)
        self.__saturationStage.configUpdated.connect(self.__configUpdated)
        self.__statisticsStage = StatisticsStage(self)
        self.__statisticsStage.configUpdated.connect(self.__configUpdated)
        self.__isoContourStage = IsoContourStage(self)
        self.__isoContourStage.configUpdated.connect(self.__configUpdated)

    def __configUpdated(self):
        self.configUpdated.emit()

    def clear(self):
        self.__maskStage.clear()
        self.__statisticsStage.clear()

    def flatFieldStage(self):
        return self.__flatFieldStage

    def exposureTimeStage(self):
        return self.__exposureTimeStage

    def maskStage(self):
        return self.__maskStage

    def saturationStage(self):
        return self.__saturationStage

    def statisticsStage(self):
        return self.__statisticsStage

    def isoContourStage(self):
        return self.__isoContourStage

    def captureRawDetector(
        self, scan: scan_model.Scan, raw: numpy.array, imageKind: ImageLayer
    ):
        self.__flatFieldStage.captureRawDetector(scan, raw=raw)

    def process(
        self, data: numpy.ndarray, imageKind: ImageLayer, exposureTime: float
    ) -> Tuple[numpy.array, List[ImageCorrections]]:

        corrections = []

        if self.__saturationStage.isEnabled():
            self.__saturationStage.correction(data)
            corrections.extend(self.__saturationStage.lastApplyedCorrections())

        if self.__maskStage.isEnabled():
            data = self.__maskStage.correction(data)
            corrections.extend(self.__maskStage.lastApplyedCorrections())

        if self.__statisticsStage.isEnabled():
            self.__statisticsStage.correction(data)
            corrections.extend(self.__statisticsStage.lastApplyedCorrections())

        if (
            imageKind != ImageLayer.DARK
            and self.__flatFieldStage.isEnabled()
            and exposureTime is not None
        ):
            data = self.__flatFieldStage.correction(
                data,
                exposureTime,
                use_flat=imageKind != ImageLayer.FLAT,
            )
            corrections.extend(self.__flatFieldStage.lastApplyedCorrections())

        if self.__exposureTimeStage.isEnabled() and exposureTime is not None:
            data = self.__exposureTimeStage.correction(data, exposureTime)
            corrections.extend(self.__exposureTimeStage.lastApplyedCorrections())

        isoContourStage = self.__isoContourStage
        if isoContourStage.isEnabled():
            isoContourStage.correction(data, self.__maskStage.mask())
            corrections.extend(self.__isoContourStage.lastApplyedCorrections())

        return data, corrections


class ImagePlotWidget(plot_helper.PlotWidget):

    HISTOGRAMS_COLOR = "blue"
    """Color to use for the side histograms."""

    HISTOGRAMS_HEIGHT = 200
    """Height in pixels of the side histograms."""

    IMAGE_MIN_SIZE = 200
    """Minimum size in pixels of the image area."""

    DEFAULT_DATA_MARGINS = 0.05, 0.05, 0.05, 0.05

    def __init__(self, parent=None):
        super(ImagePlotWidget, self).__init__(parent=parent)
        self.__scan: Optional[scan_model.Scan] = None
        self.__flintModel: Optional[flint_model.FlintState] = None
        self.__scanKind: Optional[ImageLayer] = None
        self.__plotModel: plot_model.Plot = None
        self.__deviceName: str = None
        self.__api = ImagePlotWidgetApi(self)
        self.__processing = _ImageProcessing(self)
        self.__processing.configUpdated.connect(self.__updateProcessing)

        self.__processingLock = utils.LockReentrant()

        self._cache = None  # Store currently visible data information
        self.__exposureTime = None

        self.__items: Dict[plot_model.Item, List[_ItemDescription]] = {}

        self.__plotWasUpdated: bool = False
        self.__plot = plot_helper.FlintPlot(parent=self)
        self.__plot.setActiveCurveStyle(linewidth=2)
        self.__plot.setKeepDataAspectRatio(True)
        self.__plot.setDefaultDataMargins(*self.DEFAULT_DATA_MARGINS)
        self.__plot.getYAxis().setInverted(True)
        self.__plot.sigMousePressed.connect(self.__onPlotPressed)
        plotView = self._createPlotView(self.__plot, backend=None)

        self.__roiManager = RegionOfInterestManager(self.__plot)
        self.__profileAction = None
        self.__filterAction = None

        self.__title = _Title(self.__plot)

        self.__colormap = colors.Colormap("viridis")
        """Each detector have a dedicated widget and a dedicated colormap"""
        self.__colormapInitialized = False

        self.setFocusPolicy(qt.Qt.StrongFocus)
        self.__view = view_helper.ViewManager(self.__plot)
        self.__view.setResetWhenScanStarts(False)
        self.__view.setResetWhenPlotCleared(False)

        self.__plot.sigViewChanged.connect(self.__viewChanged)

        self.__aggregator = plot_helper.PlotEventAggregator(self)
        self.__refreshManager = refresh_helper.RefreshManager(self)
        self.__refreshManager.refreshModeChanged.connect(self.__refreshModeChanged)
        self.__refreshManager.setAggregator(self.__aggregator)

        toolBar = self.__createToolBar()

        # Try to improve the look and feel
        # FIXME: This should be done with stylesheet
        line = qt.QFrame(self)
        line.setFrameShape(qt.QFrame.HLine)
        line.setFrameShadow(qt.QFrame.Sunken)

        frame = qt.QFrame(self)
        frame.setFrameShape(qt.QFrame.StyledPanel)
        frame.setAutoFillBackground(True)
        layout = qt.QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(toolBar)
        layout.addWidget(line)
        layout.addWidget(plotView)
        widget = qt.QFrame(self)
        layout = qt.QVBoxLayout(widget)
        layout.addWidget(frame)
        layout.setContentsMargins(0, 1, 0, 0)
        self.setWidget(widget)

        self.__tooltipManager = tooltip_helper.TooltipItemManager(self, self.__plot)
        self.__tooltipManager.setFilter(
            (
                plot_helper.FlintImage,
                plot_helper.FlintImageRgba,
                plot_helper.FlintImageDensityMap,
            )
        )

        self.__minMarker = Marker()
        self.__minMarker.setSymbol("")
        self.__minMarker.setVisible(False)
        self.__minMarker.setColor("black")
        self.__minMarker.setZValue(0.1)
        self.__minMarker.setName("min")

        self.__maxMarker = Marker()
        self.__maxMarker.setSymbol("")
        self.__maxMarker.setVisible(False)
        self.__maxMarker.setColor("black")
        self.__maxMarker.setZValue(0.1)
        self.__maxMarker.setName("max")

        self.__imageReceived = 0
        """Count the received image for this scan to allow to clean up the
        screen in the end if nothing was received"""

        self.__plot.addItem(self.__tooltipManager.marker())
        self.__plot.addItem(self.__minMarker)
        self.__plot.addItem(self.__maxMarker)

        self.__saturationItem = None

        self.__saturationBlink = qt.QTimer(self)
        self.__saturationBlink.setInterval(800)
        self.__saturationBlink.timeout.connect(self.__blinkSaturation)

        self.widgetActivated.connect(self.__activated)

    def __blinkSaturation(self):
        if self.__saturationItem is not None:
            self.__saturationItem.setVisible(not self.__saturationItem.isVisible())

    def event(self, event):
        result = plot_helper.PlotWidget.event(self, event)
        if event.type() == qt.QEvent.Resize:
            self.__view.widgetResized()
        elif event.type() == qt.QEvent.LayoutRequest:
            # Triggered when there is internal resize, like dock resize
            self.__view.widgetResized()
        return result

    def _createPlotView(self, plot, backend=None):
        """Setup layout around the plot."""
        self._histoHPlot = image_helper.SideHistogram(
            backend=backend, parent=self, direction=qt.Qt.Horizontal
        )
        widgetHandle = self._histoHPlot.getWidgetHandle()
        widgetHandle.setMinimumHeight(self.HISTOGRAMS_HEIGHT)
        widgetHandle.setMaximumHeight(self.HISTOGRAMS_HEIGHT)
        self._histoHPlot.setInteractiveMode("zoom")
        self._histoHPlot.setDataMargins(0.0, 0.0, 0.1, 0.1)
        self._histoHPlot.sigMouseMoved.connect(self._mouseMovedOnHistoH)
        self._histoHPlot.setProfileColor(self.HISTOGRAMS_COLOR)

        self._histoVPlot = image_helper.SideHistogram(
            backend=backend, parent=self, direction=qt.Qt.Vertical
        )
        widgetHandle = self._histoVPlot.getWidgetHandle()
        widgetHandle.setMinimumWidth(self.HISTOGRAMS_HEIGHT)
        widgetHandle.setMaximumWidth(self.HISTOGRAMS_HEIGHT)
        self._histoVPlot.setInteractiveMode("zoom")
        self._histoVPlot.setDataMargins(0.1, 0.1, 0.0, 0.0)
        self._histoVPlot.sigMouseMoved.connect(self._mouseMovedOnHistoV)
        self._histoVPlot.setProfileColor(self.HISTOGRAMS_COLOR)

        self._radarView = RadarView(parent=self)
        self._radarView.setPlotWidget(plot)

        self.__syncXAxis = SyncAxes([plot.getXAxis(), self._histoHPlot.getXAxis()])
        self.__syncYAxis = SyncAxes([plot.getYAxis(), self._histoVPlot.getYAxis()])

        plotLayout = qt.QWidget(self)
        layout = qt.QGridLayout(plotLayout)
        layout.addWidget(plot, 0, 0)
        layout.addWidget(self._histoVPlot, 0, 1)
        layout.addWidget(self._histoHPlot, 1, 0)
        layout.addWidget(self._radarView, 1, 1, 1, 2)
        # layout.addWidget(self.getColorBarWidget(), 0, 2)

        self._radarView.setMinimumWidth(self.IMAGE_MIN_SIZE)
        self._radarView.setMinimumHeight(self.HISTOGRAMS_HEIGHT)
        self._histoHPlot.setMinimumWidth(self.IMAGE_MIN_SIZE)
        self._histoVPlot.setMinimumHeight(self.HISTOGRAMS_HEIGHT)

        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 0)

        self._radarView.setVisible(False)
        self._histoHPlot.setVisible(False)
        self._histoVPlot.setVisible(False)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        return plotLayout

    def __activated(self):
        self.__initColormapWidget()

    def imageProcessing(self):
        return self.__processing

    def __initColormapWidget(self):
        flintModel = self.flintModel()
        if flintModel is None:
            return
        live = flintModel.liveWindow()
        colormapWidget = live.acquireColormapWidget(self)
        if colormapWidget is not None:
            for item in self.__plot.getItems():
                if isinstance(item, plot_helper.FlintImageMixIn):
                    if ImageLayer.MASK in item.getTags():
                        continue
                    if ImageLayer.SATURATION in item.getTags():
                        continue
                    colormapWidget.setItem(item)
                    break
            else:
                colormapWidget.setColormap(self.__colormap)

    def _mouseMovedOnHistoH(self, x, y):
        if self._cache is None:
            return
        activeImage = self.__plot.getActiveImage()
        if activeImage is None:
            return

        xOrigin = activeImage.getOrigin()[0]
        xScale = activeImage.getScale()[0]

        minValue = xOrigin + xScale * self._cache.dataXRange[0]

        if x >= minValue:
            data = self._cache.histoH
            column = int((x - minValue) / xScale)
            if False:
                if column >= 0 and column < data.shape[0]:
                    self.valueChanged.emit(
                        float("nan"),
                        float(column + self._cache.dataXRange[0]),
                        data[column],
                    )

    def _mouseMovedOnHistoV(self, x, y):
        if self._cache is None:
            return
        activeImage = self.__plot.getActiveImage()
        if activeImage is None:
            return

        yOrigin = activeImage.getOrigin()[1]
        yScale = activeImage.getScale()[1]

        minValue = yOrigin + yScale * self._cache.dataYRange[0]

        if y >= minValue:
            data = self._cache.histoV
            row = int((y - minValue) / yScale)
            if False:
                if row >= 0 and row < data.shape[0]:
                    self.valueChanged.emit(
                        float(row + self._cache.dataYRange[0]), float("nan"), data[row]
                    )

    def deviceName(self):
        return self.__deviceName

    def setDeviceName(self, name):
        self.__deviceName = name

    def configuration(self):
        config = super(ImagePlotWidget, self).configuration()
        try:
            config.colormap = self.__colormap._toDict()
        except Exception:
            # As it relies on private API, make it safe
            _logger.error("Impossible to save colormap preference", exc_info=True)

        config.profile_state = self.__profileAction.saveState()
        config.side_profile_displayed = self.isSideHistogramDisplayed()

        processing = self.__processing
        config.mask_stage = processing.maskStage().isEnabled()
        config.flatfield_stage = processing.flatFieldStage().isEnabled()
        config.statistics_stage = processing.statisticsStage().isEnabled()
        config.expotime_stage = processing.exposureTimeStage().isEnabled()
        config.saturation_stage = processing.saturationStage().isEnabled()
        config.saturation_stage_value = processing.saturationStage().value()
        return config

    def setConfiguration(self, config):
        if config.colormap is not None:
            try:
                self.__colormap._setFromDict(config.colormap)
                self.__colormapInitialized = True
            except Exception:
                # As it relies on private API, make it safe
                _logger.error(
                    "Impossible to restore colormap preference", exc_info=True
                )

        if config.profile_state is not None:
            self.__profileAction.restoreState(config.profile_state)
        if config.side_profile_displayed is not None:
            self.setSideHistogramDisplayed(config.side_profile_displayed)

        processing = self.__processing
        if config.mask_stage is not None:
            processing.maskStage().setEnabled(config.mask_stage)
        if config.flatfield_stage is not None:
            processing.flatFieldStage().setEnabled(config.flatfield_stage)
        if config.statistics_stage is not None:
            processing.statisticsStage().setEnabled(config.statistics_stage)
        if config.expotime_stage is not None:
            processing.exposureTimeStage().setEnabled(config.expotime_stage)
        if config.saturation_stage is not None:
            processing.saturationStage().setEnabled(config.saturation_stage)
        if config.saturation_stage_value is not None:
            processing.saturationStage().setValue(config.saturation_stage_value)

        super(ImagePlotWidget, self).setConfiguration(config)

    def markerAction(self):
        return self.__markerAction

    def filterAction(self):
        return self.__filterAction

    def defaultColormap(self):
        return self.__colormap

    def getRefreshManager(self) -> plot_helper.RefreshManager:
        return self.__refreshManager

    def __createToolBar(self):
        toolBar = qt.QToolBar(self)
        toolBar.setMovable(False)

        from silx.gui.plot.actions import mode
        from silx.gui.plot.actions import control
        from silx.gui.widgets.MultiModeAction import MultiModeAction

        modeAction = MultiModeAction(self)
        modeAction.addAction(mode.ZoomModeAction(self.__plot, self))
        modeAction.addAction(mode.PanModeAction(self.__plot, self))
        toolBar.addAction(modeAction)

        resetZoom = self.__view.createResetZoomAction(parent=self)
        toolBar.addAction(resetZoom)
        toolBar.addSeparator()

        # Axis
        action = self.__refreshManager.createRefreshAction(self)
        toolBar.addAction(action)
        toolBar.addAction(plot_action.CustomAxisAction(self.__plot, self, kind="image"))
        toolBar.addSeparator()

        # Item
        action = style_action.FlintSharedColormapAction(self.__plot, self)
        action.setInitColormapWidgetCallback(self.__initColormapWidget)
        toolBar.addAction(action)
        self.__contrastAction = action
        action = FilterAction(self)
        toolBar.addAction(action)
        toolBar.addSeparator()
        self.__filterAction = action

        # Tools
        self.liveAction = camera_live_action.CameraLiveAction(self)
        toolBar.addAction(self.liveAction)
        action = control.CrosshairAction(self.__plot, parent=self)
        action.setIcon(icons.getQIcon("flint:icons/crosshair"))
        toolBar.addAction(action)
        action = histogram.PixelIntensitiesHistoAction(self.__plot, self)
        icon = icons.getQIcon("flint:icons/histogram")
        action.setIcon(icon)
        toolBar.addAction(action)

        self.__profileAction = profile_action.ProfileAction(self.__plot, self, "image")
        toolBar.addAction(self.__profileAction)

        action = marker_action.MarkerAction(plot=self.__plot, parent=self, kind="image")
        self.__markerAction = action
        toolBar.addAction(action)

        action = control.ColorBarAction(self.__plot, self)
        icon = icons.getQIcon("flint:icons/colorbar")
        action.setIcon(icon)
        toolBar.addAction(action)
        toolBar.addSeparator()

        # Export

        self.__exportAction = export_action.ExportAction(self.__plot, self)
        toolBar.addAction(self.__exportAction)

        return toolBar

    def setSideHistogramDisplayed(self, show):
        """Display or not the side histograms"""
        if self.isSideHistogramDisplayed() == show:
            return
        self._histoHPlot.setVisible(show)
        self._histoVPlot.setVisible(show)
        self._radarView.setVisible(show)
        self.__profileAction.sideHistogramsDisplayedAction().setChecked(show)
        if show:
            # Probably have to be computed
            self._updateHistograms()

    def isSideHistogramDisplayed(self):
        """True if the side histograms are displayed"""
        return self._histoHPlot.isVisible()

    def __viewChanged(self):
        self._updateHistograms()

    def _updateHistograms(self):
        """Update histograms content using current active image."""
        if not self.isSideHistogramDisplayed():
            # The histogram computation can be skipped
            return

        activeImage = self.__plot.getActiveImage()
        if activeImage is not None:
            xRange = self.__plot.getXAxis().getLimits()
            yRange = self.__plot.getYAxis().getLimits()
            result = image_helper.computeProfileSumOnRange(
                activeImage, xRange, yRange, self._cache
            )
        else:
            result = None
        self._cache = result
        self._histoHPlot.setProfileSum(result)
        self._histoVPlot.setProfileSum(result)

    def logbookAction(self):
        """Expose a logbook action if one"""
        return self.__exportAction.logbookAction()

    def _silxPlot(self):
        """Returns the silx plot associated to this view.

        It is provided without any warranty.
        """
        return self.__plot

    def plotApi(self):
        """Expose dedicated API to BLISS"""
        return self.__api

    def __onPlotPressed(self):
        self.widgetActivated.emit(self)

    def createPropertyWidget(self, parent: qt.QWidget):
        useFlatImageProperty = self.__flintModel.useFlatImageProperty()
        if useFlatImageProperty:
            from .image_plot_property2 import ImagePlotProperty2Widget as PropertyWidget
        else:
            from .image_plot_property import ImagePlotPropertyWidget as PropertyWidget

        propertyWidget = PropertyWidget(parent)
        propertyWidget.setFlintModel(self.__flintModel)
        propertyWidget.setFocusWidget(self)
        return propertyWidget

    def flintModel(self) -> Optional[flint_model.FlintState]:
        return self.__flintModel

    def setFlintModel(self, flintModel: Optional[flint_model.FlintState]):
        self.__flintModel = flintModel
        self.__exportAction.setFlintModel(flintModel)
        self.__contrastAction.setFlintModel(flintModel)

        if flintModel is not None:
            if not self.__colormapInitialized:
                style = flintModel.defaultImageStyle()
                self.__colormap.setName(style.colormapLut)

    def setPlotModel(self, plotModel: plot_model.Plot):
        if self.__plotModel is not None:
            self.__plotModel.itemAdded.disconnect(
                self.__aggregator.callbackTo(self.__itemAdded)
            )
            self.__plotModel.itemRemoved.disconnect(
                self.__aggregator.callbackTo(self.__itemRemoved)
            )
            self.__plotModel.structureChanged.disconnect(
                self.__aggregator.callbackTo(self.__structureChanged)
            )
            self.__plotModel.itemValueChanged.disconnect(
                self.__aggregator.callbackTo(self.__itemValueChanged)
            )
            self.__plotModel.transactionFinished.disconnect(
                self.__aggregator.callbackTo(self.__transactionFinished)
            )
        previousPlot = self.__plotModel
        self.__plotModel = plotModel
        if self.__plotModel is not None:
            self.__plotModel.itemAdded.connect(
                self.__aggregator.callbackTo(self.__itemAdded)
            )
            self.__plotModel.itemRemoved.connect(
                self.__aggregator.callbackTo(self.__itemRemoved)
            )
            self.__plotModel.structureChanged.connect(
                self.__aggregator.callbackTo(self.__structureChanged)
            )
            self.__plotModel.itemValueChanged.connect(
                self.__aggregator.callbackTo(self.__itemValueChanged)
            )
            self.__plotModel.transactionFinished.connect(
                self.__aggregator.callbackTo(self.__transactionFinished)
            )
        self.plotModelUpdated.emit(plotModel)
        self.__updatePreferedRefreshRate(
            previousPlot=previousPlot, plot=self.__plotModel
        )
        self.__redrawAll()

    def plotModel(self) -> plot_model.Plot:
        return self.__plotModel

    def __structureChanged(self):
        self.__redrawAll()

    def __itemAdded(self, item):
        self.__updatePreferedRefreshRate(newItem=item)

    def __itemRemoved(self, item):
        self.__updatePreferedRefreshRate(previousItem=item)

    def __transactionFinished(self):
        if self.__plotWasUpdated:
            self.__plotWasUpdated = False
            self.__view.plotUpdated()

    def __itemValueChanged(
        self, item: plot_model.Item, eventType: plot_model.ChangeEventType
    ):
        if eventType == plot_model.ChangeEventType.VISIBILITY:
            self.__updateItem(item)
        elif eventType == plot_model.ChangeEventType.IMAGE_CHANNEL:
            self.__updateItem(item)
        elif eventType == plot_model.ChangeEventType.CUSTOM_STYLE:
            self.__updateItem(item)

    def scan(self) -> Optional[scan_model.Scan]:
        return self.__scan

    def setScan(self, scan: scan_model.Scan = None):
        if self.__scan is scan:
            return
        self.liveAction.setScan(scan)
        if self.__scan is not None:
            self.__scan.scanDataUpdated[object].disconnect(
                self.__aggregator.callbackTo(self.__scanDataUpdated)
            )
            self.__scan.scanStarted.disconnect(
                self.__aggregator.callbackTo(self.__scanStarted)
            )
            self.__scan.scanFinished.disconnect(
                self.__aggregator.callbackTo(self.__scanFinished)
            )
        self.__title.scanRemoved(self.__scan)
        previousScan = self.__scan
        self.__scan = scan
        # As the scan was updated, clear the previous cached events
        self.__aggregator.clear()
        if self.__scan is not None:
            self.__scan.scanDataUpdated[object].connect(
                self.__aggregator.callbackTo(self.__scanDataUpdated)
            )
            self.__scan.scanStarted.connect(
                self.__aggregator.callbackTo(self.__scanStarted)
            )
            self.__scan.scanFinished.connect(
                self.__aggregator.callbackTo(self.__scanFinished)
            )
            if self.__scan.state() != scan_model.ScanState.INITIALIZED:
                self.__title.scanStarted(self.__scan)
        self.scanModelUpdated.emit(scan)

        # Note: No redraw here to avoid blinking of the image
        # The image title is explicitly tagged as "outdated"
        # To avoid mistakes
        self.__updatePreferedRefreshRate(previousScan=previousScan, scan=self.__scan)
        self.__redrawAllIfNeeded()

    def __refreshModeChanged(self):
        self.__updatePreferedRefreshRate()

    def __updatePreferedRefreshRate(
        self,
        previousScan: scan_model.Scan = None,
        scan: scan_model.Scan = None,
        previousPlot: plot_model.Plot = None,
        plot: plot_model.Plot = None,
        previousItem: plot_model.Item = None,
        newItem: plot_model.Item = None,
    ):
        """Propagate prefered refresh rate to the internal scan model.

        This allow the scan manager to optimize image download.

        The function deals with all the cases which can happen. Changes of the
        scan, the plot, or the items. Item visibility could also be taken into
        account.
        """

        if plot is None:
            plot = self.__plotModel
        if scan is None:
            scan = self.__scan

        key = self.objectName()

        def imageChannels(plotModel, scan):
            """Iterate through all channel scan from image items"""
            for item in plotModel.items():
                if isinstance(item, plot_item_model.ImageItem):
                    channelRef = item.imageChannel()
                    if channelRef is None:
                        continue
                    channel = channelRef.channel(scan)
                    if channel is None:
                        continue
                    yield channel

        # Remove preferences from the previous plot
        if previousPlot is not None and scan is not None:
            for channel in imageChannels(previousPlot, scan):
                channel.setPreferedRefreshRate(key, None)

        if plot is None:
            return

        # Remove preferences from the previous scan
        if previousScan is not None:
            for channel in imageChannels(plot, previousScan):
                channel.setPreferedRefreshRate(key, None)

        rate = self.__refreshManager.refreshMode()

        if scan is not None:
            # Remove preferences from the prevouos item
            if previousItem is not None:
                item = previousItem
                if isinstance(item, plot_item_model.ImageItem):
                    channelRef = item.imageChannel()
                    if channelRef is not None:
                        channel = channelRef.channel(scan)
                        if channel is not None:
                            channel.setPreferedRefreshRate(key, None)
            elif newItem is not None:
                item = newItem
                if isinstance(item, plot_item_model.ImageItem):
                    channelRef = item.imageChannel()
                    if channelRef is not None:
                        channel = channelRef.channel(scan)
                        if channel is not None:
                            channel.setPreferedRefreshRate(key, rate)
            else:
                # Update the preferences to the current plot and current scan
                for channel in imageChannels(plot, scan):
                    channel.setPreferedRefreshRate(key, rate)

    def __scanStarted(self):
        self.__imageReceived = 0
        self.__createScanRois()
        self.__refreshManager.scanStarted()
        self.__view.scanStarted()
        info = extract_exposure_time(self.__scan.scanInfo())
        self.__scanKind, self.__exposureTime = info
        self.__title.scanStarted(self.__scan)
        self.__processing.clear()

    def __scanFinished(self):
        self.__refreshManager.scanFinished()
        if self.__imageReceived == 0:
            self.__cleanAll()
        self.__title.scanFinished(self.__scan)

    def __createScanRois(self):
        self.__roiManager.clear()
        if self.__scan is None:
            return

        limaDevice = None
        for device in self.__scan.devices():
            if device.type() != scan_model.DeviceType.LIMA:
                continue
            if device.name() == self.deviceName():
                limaDevice = device
                break

        if limaDevice is None:
            return

        for device in limaDevice.devices():
            roi = device.metadata().roi
            if roi is None:
                continue

            item = roi_helper.limaRoiToScanRoi(roi)
            if item is not None:
                self.__roiManager.addRoi(item)
                item.setName(device.name())
                item.setEditable(False)
                item.setSelectable(False)
                item.setColor(qt.QColor(0x80, 0x80, 0x80))
                item.setVisible(False)

    def __scanDataUpdated(self, event: scan_model.ScanDataUpdateEvent):
        plotModel = self.__plotModel
        if plotModel is None:
            return
        self.__imageReceived += 1
        for item in plotModel.items():
            if isinstance(item, plot_item_model.ImageItem):
                channelName = item.imageChannel().name()
                if event.isUpdatedChannelName(channelName):
                    self.__updateItem(item)
            elif isinstance(item, plot_item_model.RoiItem):
                self.__updateItem(item)

    def updateAll(self):
        self.__updateAll()

    def __updateProcessing(self):
        if self.__processingLock.locked():
            return
        self.__updateAll()

    def __updateAll(self):
        plotModel = self.__plotModel
        if plotModel is None:
            return
        for item in plotModel.items():
            if isinstance(item, plot_item_model.ImageItem):
                self.__updateItem(item)
            elif isinstance(item, plot_item_model.RoiItem):
                self.__updateItem(item)

    def __cleanAll(self):
        for _item, itemKeys in self.__items.items():
            for description in itemKeys:
                self.__plot.remove(description.key, description.kind)
        self.__view.plotCleared()

    def __cleanItem(self, item: plot_model.Item):
        itemKeys = self.__items.pop(item, [])
        if len(itemKeys) == 0:
            return False
        for description in itemKeys:
            self.__plot.remove(description.key, description.kind)
        return True

    def __redrawAllIfNeeded(self):
        plotModel = self.__plotModel
        if plotModel is None or self.__scan is None:
            self.__cleanAll()
            return

        for item in plotModel.items():
            if not isinstance(item, plot_item_model.ImageItem):
                continue
            if not item.isVisible():
                continue
            data = item.imageChannel().data(self.__scan)
            if data is None:
                continue
            self.__redrawAll()

    def __redrawAll(self):
        self.__cleanAll()
        plotModel = self.__plotModel
        if plotModel is None:
            return

        for item in plotModel.items():
            self.__updateItem(item)

    def __updateItem(self, item: plot_model.Item):
        """Update the items without reseting the view"""
        if self.__plotModel is None:
            return
        if self.__scan is None:
            return
        if not item.isValid():
            return
        if isinstance(item, plot_item_model.ImageItem):
            self.__updateImageItem(item)
        elif isinstance(item, plot_item_model.RoiItem):
            roi_name = item.roiName()
            roi = [r for r in self.__roiManager.getRois() if r.getName() == roi_name]
            roi = roi[0] if len(roi) > 0 else None
            if roi is not None:
                roi.setVisible(item.isVisible())

    def __updateImageItem(self, item: plot_model.Item):
        scan = self.__scan
        plot = self.__plot
        plotItems: List[_ItemDescription] = []

        updateZoomNow = not self.__plotModel.isInTransaction()

        wasUpdated = self.__cleanItem(item)

        if not item.isVisible():
            if wasUpdated:
                self.__updatePlotZoom(updateZoomNow)
            return

        if not item.isValidInScan(scan):
            if wasUpdated:
                self.__updatePlotZoom(updateZoomNow)
            return

        dataChannel = item.imageChannel()
        if dataChannel is None:
            self.__cleanItem(item)
            return
        image = dataChannel.array(self.__scan)
        if image is None:
            if wasUpdated:
                self.__updatePlotZoom(updateZoomNow)
            return
        raw = image

        with self.__processingLock:
            self.__processing.captureRawDetector(scan, image, imageKind=self.__scanKind)

        legend = dataChannel.name()
        style = item.getStyle(self.__scan)
        colormap = model_helper.getColormapFromItem(item, style, self.__colormap)

        live = self.flintModel().liveWindow()
        if live is not None:
            colormapWidget = live.ownedColormapWidget(self)
        else:
            colormapWidget = None

        image, corrections = self.__processing.process(
            image, imageKind=self.__scanKind, exposureTime=self.__exposureTime
        )

        if style.symbolStyle is style_model.SymbolStyle.NO_SYMBOL:
            if image.ndim == 3:
                imageItem = plot_helper.FlintImageRgba()
            else:
                densityMethod = self.__filterAction.densityMethod()
                if densityMethod is None:
                    imageItem = plot_helper.FlintImage()
                else:
                    imageItem = plot_helper.FlintImageDensityMap()
                    imageItem.setAggregationMode(densityMethod)
                imageItem.setColormap(colormap)

            imageItem.setData(image, copy=False)
            if raw is not image:
                imageItem.setRawData(raw)
            imageItem.setTags(corrections)
            imageItem.setCustomItem(item)
            imageItem.setScan(scan)
            imageItem.setName(legend)
            self.__plot.addItem(imageItem)

            if colormapWidget is not None:
                if isinstance(imageItem, plot_helper.FlintImageRgba):
                    colormapWidget.setItem(None)
                else:
                    colormapWidget.setItem(imageItem)

            self.__plot.setActiveImage(legend)
            plotItems.append(_ItemDescription(legend, "image", image.shape))
            self.__title.itemUpdated(
                scan, item, kind=self.__scanKind, corrections=corrections
            )

            bottom, left = 0, 0
            height, width = image.shape[0], image.shape[1]
            self.__minMarker.setPosition(0, 0)
            self.__minMarker.setText(f"{left}, {bottom}")
            self.__minMarker.setVisible(True)
            self.__maxMarker.setPosition(width, height)
            self.__maxMarker.setText(f"{width}\n{height}")
            self.__maxMarker.setVisible(True)
        else:
            yy = numpy.atleast_2d(numpy.arange(image.shape[0])).T
            xx = numpy.atleast_2d(numpy.arange(image.shape[1]))
            xx = xx * numpy.atleast_2d(numpy.ones(image.shape[0])).T + 0.5
            yy = yy * numpy.atleast_2d(numpy.ones(image.shape[1])) + 0.5
            image, xx, yy = image.reshape(-1), xx.reshape(-1), yy.reshape(-1)
            key = plot.addScatter(
                x=xx, y=yy, value=image, legend=legend, colormap=colormap
            )
            scatter = plot.getScatter(key)
            symbolStyle = style_model.symbol_to_silx(style.symbolStyle)
            if symbolStyle == " ":
                symbolStyle = "o"
            scatter.setSymbol(symbolStyle)
            scatter.setSymbolSize(style.symbolSize)
            plotItems.append(_ItemDescription(key, "scatter", image.shape))

        maskStage = self.__processing.maskStage()
        mask = None
        if maskStage.isMaskDisplayedAsLayer() and maskStage.isValid():
            densityMethod = self.__filterAction.densityMethod()
            if densityMethod is None:
                maskItem = plot_helper.FlintImage()
            else:
                maskItem = plot_helper.FlintImageDensityMap()
                maskItem.setAggregationMode(
                    plot_helper.FlintImageDensityMap.Aggregation.MAX
                )
            maskItem.setTags([ImageLayer.MASK])

            mask = maskStage.mask()
            maskImage = numpy.empty(shape=mask.shape, dtype=numpy.float16)
            maskImage[:, :] = numpy.nan
            maskImage[mask] = 1

            def createMaskColormap(colormap):
                """Returns a colormap for a mask derived from a source colormap.

                This will not be updated during a change of the original colormap,
                but it's a very small rendering issue. It could be fixed with a
                callback.
                """
                cursor = colors.cursorColorForColormap(colormap.getName())
                colorlist = ["black", cursor]
                colorlist = [colors.rgba(c) for c in colorlist]
                maskColormap = colors.Colormap(colors=colorlist, vmin=0, vmax=1)
                return maskColormap

            maskColormap = createMaskColormap(colormap)
            maskItem.setColormap(maskColormap)
            maskItem.setData(maskImage, copy=False)
            maskItem.setCustomItem(item)
            maskItem.setScan(scan)
            maskItem.setName(legend + "__mask")
            self.__plot.addItem(maskItem)
            plotItems.append(
                _ItemDescription(legend + "__mask", "image", maskImage.shape)
            )

        isoContourStage = self.__processing.isoContourStage()
        if isoContourStage.isEnabled():
            polygons = isoContourStage.isoContours()
            _logger.error(str(polygons))
            if polygons is not None:
                for ipolygon, polygon in enumerate(polygons):
                    if len(polygon) == 0:
                        continue
                    # is_closed = numpy.allclose(polygon[0], polygon[-1])
                    x = polygon[:, 1] + 0.5
                    y = polygon[:, 0] + 0.5
                    key = f"{legend}__isosurface_{ipolygon}"
                    self.__plot.addCurve(
                        x=x,
                        y=y,
                        legend=key,
                        resetzoom=False,
                        color="black",
                        linestyle="--",
                    )
                    plotItems.append(_ItemDescription(key, "curve", image.shape))

        saturationStage = self.__processing.saturationStage()
        saturation = None
        if saturationStage.isEnabled() and saturationStage.saturationMask() is not None:
            densityMethod = self.__filterAction.densityMethod()
            if densityMethod is None:
                saturationItem = plot_helper.FlintImage()
            else:
                saturationItem = plot_helper.FlintImageDensityMap()
                saturationItem.setAggregationMode(
                    plot_helper.FlintImageDensityMap.Aggregation.MAX
                )
            saturationItem.setTags([ImageLayer.SATURATION])

            saturation = saturationStage.saturationMask()
            saturationImage = numpy.empty(shape=saturation.shape, dtype=numpy.float16)
            saturationImage[:, :] = numpy.nan
            saturationImage[saturation] = 1

            def createMaskColormap(colormap):
                """Returns a colormap for a mask derived from a source colormap.

                This will not be updated during a change of the original colormap,
                but it's a very small rendering issue. It could be fixed with a
                callback.
                """
                colorlist = ["black", "#FF000090"]
                colorlist = [colors.rgba(c) for c in colorlist]
                maskColormap = colors.Colormap(colors=colorlist, vmin=0, vmax=1)
                return maskColormap

            saturationColormap = createMaskColormap(colormap)
            saturationItem.setColormap(saturationColormap)
            saturationItem.setData(saturationImage, copy=False)
            saturationItem.setCustomItem(item)
            saturationItem.setScan(scan)
            saturationItem.setName(legend + "__saturation")
            self.__plot.addItem(saturationItem)
            plotItems.append(
                _ItemDescription(
                    legend + "__saturation", "image", saturationImage.shape
                )
            )
            if self.__saturationItem is None:
                self.__saturationBlink.start()
            self.__saturationItem = saturationItem
        else:
            if self.__saturationItem is not None:
                self.__saturationBlink.stop()
            self.__saturationItem = None

        self._cache = None
        self._updateHistograms()

        self.__items[item] = plotItems
        self.__updatePlotZoom(updateZoomNow)

    def __updatePlotZoom(self, updateZoomNow):
        if updateZoomNow:
            self.__view.plotUpdated()
        else:
            self.__plotWasUpdated = True
