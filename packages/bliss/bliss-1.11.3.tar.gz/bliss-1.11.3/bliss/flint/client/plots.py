# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Provides plot helper class to deal with flint proxy.
"""

import typing

import numpy
import contextlib
import logging

from bliss.common import deprecation
from .base_plot import BasePlot
from .live_image_plot import LiveImagePlot
from .live_scatter_plot import LiveScatterPlot
from .live_curve_plot import LiveCurvePlot
from .live_mca_plot import LiveMcaPlot
from .live_onedim_plot import LiveOneDimPlot

_logger = logging.getLogger(__name__)


class _DataPlot(BasePlot):
    """
    Plot providing a common API to store data

    This was introduced for baward compatibility with BLISS <= 1.8

    FIXME: This have to be deprecated and removed. Plots should be updated using
    another API
    """

    # Data handling

    def upload_data(self, field, data):
        """
        Update data as an identifier into the server side

        Argument:
            field: Identifier in the targeted plot
            data: Data to upload
        """
        deprecation.deprecated_warning(
            "Method", "upload_data", replacement="set_data", since_version="1.9"
        )
        return self.submit("updateStoredData", field, data)

    def upload_data_if_needed(self, field, data):
        """Upload data only if it is a numpy array or a list"""
        deprecation.deprecated_warning(
            "Method",
            "upload_data_if_needed",
            replacement="set_data",
            since_version="1.9",
        )
        if isinstance(data, (numpy.ndarray, list)):
            self.submit("updateStoredData", field, data)
            return field
        else:
            return data

    def add_data(self, data, field="default"):
        # Get fields
        deprecation.deprecated_warning(
            "Method", "add_data", replacement="set_data", since_version="1.9"
        )
        if isinstance(data, dict):
            fields = list(data)
        else:
            fields = numpy.array(data).dtype.fields
        # Single data
        if fields is None:
            data_dict = dict([(field, data)])
        # Multiple data
        else:
            data_dict = dict((field, data[field]) for field in fields)
        # Send data
        for field, value in data_dict.items():
            self.upload_data(field, value)
        # Return data dict
        return data_dict

    def remove_data(self, field):
        self.submit("removeStoredData", field)

    def select_data(self, *names, **kwargs):
        deprecation.deprecated_warning(
            "Method",
            "select_data",
            replacement="set_data/add_curve/add_curve_item/set_data",
            since_version="1.9",
        )
        self.submit("selectStoredData", *names, **kwargs)

    def deselect_data(self, *names):
        deprecation.deprecated_warning(
            "Method",
            "deselect_data",
            replacement="set_data/add_curve/add_curve_item",
            since_version="1.9",
        )
        self.submit("deselectStoredData", *names)

    def clear_data(self):
        self.submit("clear")

    def get_data(self, field=None):
        return self.submit("getStoredData", field=field)


# Plot classes


class Plot1D(_DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.custom_plots.silx_plots.Plot1D"

    # Available name to identify this plot
    ALIASES = ["curve", "plot1d"]

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

    def add_curve(self, x, y, **kwargs):
        """
        Create a curve in this plot.
        """
        if x is None:
            x = numpy.arange(len(y))
        if y is None:
            raise ValueError("A y value is expected. None found.")
        self.submit("addCurve", x, y, **kwargs)

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

    def set_xaxis_scale(self, value):
        """
        Set the X-axis scale of this plot.

        Deprecated in BLISS 1.10. prefer using `xscale` property

        Argument:
            value: One of "linear" or "log"
        """
        self.xscale = value

    def set_yaxis_scale(self, value):
        """
        Set the Y-axis scale of this plot.

        Deprecated in BLISS 1.10. prefer using `xscale` property

        Argument:
            value: One of "linear" or "log"
        """
        self.yscale = value

    def clear_items(self):
        """Remove all the items described in this plot

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("clearItems")

    def add_curve_item(self, xname: str, yname: str, legend: str = None, **kwargs):
        """Define a specific curve item

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("addCurveItem", xname, yname, legend=legend, **kwargs)

    def get_item(self, legend):
        """Get the description of an item"""
        return self.submit("getItem", legend=legend)

    def remove_item(self, legend: str):
        """Remove a specific item.

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("removeItem", legend)

    def item_exists(self, legend: str):
        """True if a specific item exists."""
        return self.submit("itemExists", legend)

    def set_data(self, **kwargs):
        """Set data named from keys with associated values.

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("setData", **kwargs)

    def append_data(self, **kwargs):
        """Append data named from keys with associated values.

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("appendData", **kwargs)

    @contextlib.contextmanager
    def transaction(self, resetzoom=True):
        """Context manager to handle a set of changes and a single refresh of
        the plot. This is needed cause the action are done on the plot
        asynchronously"""
        self.submit("setAutoUpdatePlot", False)
        try:
            yield
        finally:
            self.submit("setAutoUpdatePlot", True)
            self.submit("updatePlot", resetzoom=resetzoom)

    def select_points_to_remove(self, legend: str, data_names=None) -> bool:
        """Start a user selection to remove points from the UI.

        The interaction can be stoped from the UI or by a ctrl-c

        The result can be retrieved with the `get_data(name_of_the_data)`.

        Arguments:
            legend: The name of the curve item in which points have to be removed
            data_names: An optional list of data name which also have to be updated
        """
        desc = self.get_item(legend)
        x_name, y_name = desc["xdata"], desc["ydata"]
        style = desc["style"]
        self.add_curve_item(
            x_name, y_name, legend=legend, linestyle="-", symbol="o", linewidth=2
        )
        previous_data = {x_name: self.get_data(x_name), y_name: self.get_data(y_name)}
        if data_names is not None:
            for n in data_names:
                previous_data[n] = self.get_data(n)
        try:
            while True:
                res = self.select_shape("rectangle", valid=True, cancel=True)
                if res is False:
                    raise KeyboardInterrupt()
                if res is True:
                    break
                rect = res
                assert len(rect) == 2
                range_x = sorted([rect[0][0], rect[1][0]])
                range_y = sorted([rect[0][1], rect[1][1]])
                # mask on everything outside the rect
                x = self.get_data(x_name)
                y = self.get_data(y_name)
                i = numpy.logical_or(
                    numpy.logical_or(x < range_x[0], x > range_x[1]),
                    numpy.logical_or(y < range_y[0], y > range_y[1]),
                )
                data = {x_name: x[i], y_name: y[i]}
                if data_names is not None:
                    for n in data_names:
                        data[n] = self.get_data(n)[i]
                self.set_data(**data)
        except KeyboardInterrupt:
            self.set_data(**previous_data)
            return False
        finally:
            self.add_curve_item(x_name, y_name, legend=legend, **style)
        return True


class ScatterView(_DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.custom_plots.silx_plots.ScatterView"

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


class ScatterView3D(_DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.custom_plots.silx_plots.ScatterView3D"

    # Available name to identify this plot
    ALIASES = ["scatter3d"]

    def _init(self):
        # Make it public
        self.set_colormap = self._set_colormap

    def set_marker(self, symbol):
        """
        Set the kind of marker to use for scatters.

        Attributes:
            symbol: One of '.', ',', 'o'.
        """
        self.submit("setMarker", symbol)

    def set_data(self, x, y, z, value):
        if x is None or y is None or z is None or value is None:
            self.clear_data()
        else:
            self.submit("setData", x, y, z, value)


class Plot2D(_DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.custom_plots.silx_plots.Plot2D"

    # Available name to identify this plot
    ALIASES = ["plot2d"]

    def _init(self):
        # Make it public
        self.set_colormap = self._set_colormap

    def _init_plot(self):
        super(Plot2D, self)._init_plot()
        self.submit("setKeepDataAspectRatio", True)
        self.submit("setDisplayedIntensityHistogram", True)

    @property
    def yaxis_direction(self) -> str:
        """Direction of the y-axis.

        One of "up", "down"
        """
        return self.submit("getYaxisDirection")

    @yaxis_direction.setter
    def yaxis_direction(self, direction: str):
        self.submit("setYaxisDirection", direction)

    def add_image(self, data, **kwargs):
        self.submit("addImage", data, **kwargs)

    def select_mask(self, initial_mask: numpy.ndarray = None, directory: str = None):
        """Request a mask image from user selection.

        Argument:
            initial_mask: An initial mask image, else None
            directory: Directory used to import/export masks

        Return:
            A numpy array containing the user mask image
        """
        flint = self._flint
        request_id = flint.request_select_mask_image(
            self._plot_id, initial_mask, directory=directory
        )
        return self._wait_for_user_selection(request_id)


class Plot3D(_DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.custom_plots.silx_plots.Plot3D"

    # Available name to identify this plot
    ALIASES = ["3d", "plot3d"]

    def add_scatter_item(
        self,
        x: str,
        y: str,
        z: str,
        v: str,
        legend: str = None,
        symbol: str = ",",
        symbol_size=None,
        lut=None,
        vmin=None,
        vmax=None,
    ):
        """
        Create a scatter item in the plot.
        """
        self.submit(
            "addScatterItem",
            x,
            y,
            z,
            v,
            legend=legend,
            symbol=symbol,
            symbolSize=symbol_size,
            lut=lut,
            vmin=vmin,
            vmax=vmax,
        )

    def add_mesh_item(
        self,
        vertices: str,
        faces: str,
        legend: str = None,
        color: numpy.ndarray = None,
    ):
        """
        Create a mesh item in the plot.
        """
        self.submit(
            "addMeshItem", vertices=vertices, faces=faces, legend=legend, color=color
        )

    def clear_items(self):
        """Remove all the items described in this plot

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("clearItems")

    def reset_zoom(self):
        """Reset the zoom of the camera."""
        self.submit("resetZoom")

    def remove_item(self, legend: str):
        """Remove a specific item.

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("removeItem", legend)

    def set_data(self, **kwargs):
        """Set data named from keys with associated values.

        If no transaction was open, it will update the plot and refresh the plot
        view.
        """
        self.submit("setData", **kwargs)

    @contextlib.contextmanager
    def transaction(self, resetzoom=True):
        """Context manager to handle a set of changes and a single refresh of
        the plot. This is needed cause the action are done on the plot
        asynchronously"""
        self.submit("setAutoUpdatePlot", False)
        try:
            yield
        finally:
            self.submit("setAutoUpdatePlot", True)
            self.submit("updatePlot", resetzoom=resetzoom)


class CurveStack(BasePlot):
    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.custom_plots.curve_stack.CurveStack"

    # Available name to identify this plot
    ALIASES = ["curvestack"]

    def set_data(self, curves, x=None, reset_zoom=None):
        """
        Set the data displayed in this plot.

        Arguments:
            curves: The data of the curves (first dim is curve index, second dim
                    is the x index)
            x: Mapping of the real X axis values to use
            reset_zoom: If True force reset zoom, else the user selection is
                        applied
        """
        self.submit("setData", data=curves, x=x, resetZoom=reset_zoom)

    def clear_data(self):
        self.submit("clear")


class TimeCurvePlot(BasePlot):
    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.custom_plots.time_curve_plot.TimeCurvePlot"

    # Available name to identify this plot
    ALIASES = ["timecurveplot"]

    def select_x_axis(self, name: str):
        """
        Select the x-axis to use

        Arguments:
            name: Name of the data to use as x-axis
        """
        self.submit("setXName", name)

    @property
    def xaxis_duration(self):
        return self.submit("xDuration")

    @xaxis_duration.setter
    def xaxis_duration(self, second: int):
        """
        Select the x-axis duration in second

        Arguments:
            second: Amount of seconds displayed in the x-axis
        """
        self.submit("setXDuration", second)

    def select_x_duration(self, second: int):
        """
        Select the x-axis duration in second

        Arguments:
            second: Amount of seconds displayed in the x-axis
        """
        self.xaxis_duration = second

    @property
    def ttl(self):
        return self.submit("ttl")

    @ttl.setter
    def ttl(self, second: int):
        """
        Set the time to live of the data.

        After this period of time, a received data is not anymore displayable
        in Flint.

        Arguments:
            second: Amount of seconds a data will live
        """
        self.submit("setTtl", second)

    def add_time_curve_item(self, yname, **kwargs):
        """
        Select a dedicated data to be displayed against the time.

        Arguments:
            name: Name of the data to use as y-axis
            kwargs: Associated style (see `addCurve` from silx plot)
        """
        self.submit("addTimeCurveItem", yname, **kwargs)

    def set_data(self, **kwargs):
        """
        Set the data displayed in this plot.

        Arguments:
            kwargs: Name of the data associated to the new numpy array to use
        """
        self.submit("setData", **kwargs)

    def append_data(self, **kwargs):
        """
        Append the data displayed in this plot.

        Arguments:
            kwargs: Name of the data associated to the numpy array to append
        """
        self.submit("appendData", **kwargs)

    def clear_data(self):
        self.submit("clear")


class ImageView(_DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.custom_plots.silx_plots.ImageView"

    # Available name to identify this plot
    ALIASES = ["image", "imageview", "histogramimage"]

    def _init(self):
        # Make it public
        self.set_colormap = self._set_colormap

    def _init_plot(self):
        super(ImageView, self)._init_plot()
        self.submit("setKeepDataAspectRatio", True)
        self.submit("setDisplayedIntensityHistogram", True)

    @property
    def yaxis_direction(self) -> str:
        """Direction of the y-axis.

        One of "up", "down"
        """
        return self.submit("getYaxisDirection")

    @yaxis_direction.setter
    def yaxis_direction(self, direction: str):
        self.submit("setYaxisDirection", direction)

    def set_data(self, data, **kwargs):
        if "origin" in kwargs:
            if kwargs["origin"] is None:
                # Enforce the silx default
                del kwargs["origin"]
        if "scale" in kwargs:
            if kwargs["scale"] is None:
                # Enforce the silx default
                del kwargs["scale"]
        self.submit("setImage", data, **kwargs)

    @property
    def side_histogram_displayed(self) -> bool:
        return self.submit("isSideHistogramDisplayed")

    @side_histogram_displayed.setter
    def side_histogram_displayed(self, displayed: bool):
        self.submit("setSideHistogramDisplayed", displayed)


class StackView(_DataPlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.custom_plots.silx_plots.StackImageView"

    # Available name to identify this plot
    ALIASES = ["stack", "imagestack", "stackview"]

    def _init(self):
        # Make it public
        self.set_colormap = self._set_colormap

    def set_data(self, data, **kwargs):
        self.submit("setStack", data, **kwargs)


class SpectroPlot(BasePlot):
    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.custom_plots.spectro_plot.SpectroPlot"

    # Available name to identify this plot
    ALIASES = ["spectroplot"]

    def set_data(self, **kwargs):
        """
        Set the data displayed in this plot.

        Arguments:
            kwargs: Name of the data associated to the new numpy array to use
        """
        self.submit("setData", **kwargs)

    def add_data(self, **kwargs):
        self.submit("addData", **kwargs)

    def clear_data(self):
        self.submit("clear")

    def refresh(self):
        self.submit("refresh")

    def set_box_min_max(self, mini, maxi):
        self.submit("setBoxMinMax", mini, maxi)


class GridContainer(BasePlot):

    # Name of the corresponding silx widget
    WIDGET = "bliss.flint.custom_plots.grid_container.GridContainer"

    # Available name to identify this plot
    ALIASES = ["grid"]

    def get_plot(
        self,
        plot_class: typing.Union[str, object],
        name: str = None,
        unique_name: str = None,
        selected: bool = False,
        closeable: bool = True,
        row: int = None,
        col: int = None,
        row_span: int = None,
        col_span: int = None,
    ):
        """Create or retrieve a plot from this flint instance.

        If the plot does not exists, it will be created in a new tab on Flint.

        Arguments:
            plot_class: A class defined in `bliss.flint.client.plot`, or a
                silx class name. Can be one of "Plot1D", "Plot2D", "ImageView",
                "StackView", "ScatterView".
            name: Not applicable for this container
            unique_name: If defined the plot can be retrieved from flint.
            selected: Not applicable for this container
            closeable: Not applicable for this container
            row: Row number where to place the new widget
            col: Column number where to place the new widget
            row_span: Number of rows to use to place the new widget
            col_span: Number of columns to use to place the new widget
        """
        return self._flint.get_plot(
            plot_class=plot_class,
            name=name,
            selected=selected,
            closeable=closeable,
            unique_name=unique_name,
            parent_id=self._plot_id,
            parent_layout_params=(row, col, row_span, col_span),
        )

    @contextlib.contextmanager
    def hide_context(self):
        self.submit("setVisible", False)
        try:
            yield
        finally:
            try:
                self.submit("setVisible", True)
            except Exception:
                pass


CUSTOM_CLASSES = [
    Plot1D,
    Plot2D,
    Plot3D,
    ScatterView,
    ScatterView3D,
    ImageView,
    StackView,
    CurveStack,
    TimeCurvePlot,
    SpectroPlot,
    GridContainer,
]

LIVE_CLASSES = [
    LiveCurvePlot,
    LiveImagePlot,
    LiveScatterPlot,
    LiveMcaPlot,
    LiveOneDimPlot,
]

# For compatibility
CurvePlot = Plot1D
ImagePlot = Plot2D
ScatterPlot = ScatterView
HistogramImagePlot = ImageView
ImageStackPlot = StackView
