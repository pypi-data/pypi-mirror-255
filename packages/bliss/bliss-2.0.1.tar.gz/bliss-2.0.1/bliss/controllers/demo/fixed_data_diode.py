import os
import numpy
from bliss.common.counter import SoftCounter, SamplingMode
from bliss.common.protocols import CounterContainer
from bliss.controllers.counter import counter_namespace
from bliss.common.utils import autocomplete_property
from bliss.common.soft_axis import SoftAxis


class IdealAxis:
    def __init__(self):
        self._pos = 0

    @property
    def position(self):
        return self._pos

    @position.setter
    def position(self, pos):
        self._pos = pos


class FixedDataDiode(CounterContainer):
    """Controller with a diode emitting an fixed 1D signal read from a file."""

    def __init__(self, name, config):
        self._name = name
        filename = config.get("data_filename")
        if filename:
            data = self._load_data(filename)
        else:
            data = numpy.array(config["data"])
        self._x, self._y = data.T

        self.axis = SoftAxis(config["axis"], IdealAxis())
        self.counter = SoftCounter(
            self, self._read_signal, name=self._name, mode=SamplingMode.SINGLE
        )

    def _load_data(self, filename):
        """Load the filename as a numpy array"""
        filename = os.path.expandvars(filename)
        if not os.path.isfile(filename):
            raise RuntimeError(f"Cannot find file {filename}")
        return numpy.loadtxt(filename)

    @autocomplete_property
    def counters(self):
        return counter_namespace([self.counter])

    def _read_signal(self):
        return numpy.interp(
            self.axis.dial, self._x, self._y, left=self._y[0], right=self._y[-1]
        )
