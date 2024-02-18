# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""Module creating model around python logging library
"""
import logging
import weakref
import sys
import copy
import collections
from silx.gui import qt


class _QtLogHandler(logging.Handler):
    def __init__(self, model):
        logging.Handler.__init__(self)
        self.__model: LoggingModel = weakref.ref(model)

    def model(self):
        """
        Returns the model widget connected to this handler.

        The result can be None.
        """
        return self.__model()

    def emit(self, record: logging.LogRecord):
        """Receive a new log record."""
        model = self.model()
        if model is None:
            return
        try:
            model.appendRecord(record)
        except Exception:
            self.handleError(record)

    def handleError(self, record: logging.LogRecord):
        model = self.model()
        if model is None:
            return
        r = logging.LogRecord(
            name="bliss.flint.model.logging_model",
            level=logging.CRITICAL,
            pathname=__file__,
            lineno=45,
            msg="Error while recording new records",
            args=tuple(),
            exc_info=sys.exc_info(),
        )
        model.appendRecord(r)


class LoggingModel(qt.QObject):
    """Provides a light layer to receive and store a cache of logging records
    and few commands to edit the loggers configuration."""

    recordReceived = qt.Signal(object)

    levelConfigHaveChanged = qt.Signal(str)

    levelsConfigHaveChanged = qt.Signal()

    def __init__(self, parent=None):
        super(LoggingModel, self).__init__(parent=parent)
        self.__records = collections.deque()
        self.__maximumLogCount = 200
        self.__handlers = weakref.WeakKeyDictionary()
        qt.QCoreApplication.instance().aboutToQuit.connect(self.disconnectAll)

    def setMaximumLogCount(self, maximum: int):
        self.__maximumLogCount = maximum

    def maximumLogCount(self) -> int:
        return self.__maximumLogCount

    def records(self):
        return list(self.__records)

    def appendRecord(self, record: logging.LogRecord):
        """Add a record to the widget.

        The update of the display is done asynchronously
        """
        self.__records.append(record)
        if len(self.__records) > self.__maximumLogCount:
            self.__records.pop()

        # Precache the result
        msg = record.getMessage()
        record = copy.copy(record)
        record.getMessage = lambda: msg
        self.recordReceived.emit(record)

    def connectRootLogger(self):
        """
        Connect this model to the root logger.
        """
        self.connectLogger(logging.root)

    def connectLogger(self, logger: logging.Logger):
        """
        Connect this model to a specific logger.
        """
        handler = _QtLogHandler(self)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        )
        logger.addHandler(handler)
        self.__handlers[handler] = logger

    def disconnectAll(self):
        for handler, logger in self.__handlers.items():
            logger.removeHandler(handler)
        self.__handlers = {}

    def setLevel(self, name, level):
        """
        Change the level of a logger.
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)
        self.levelConfigHaveChanged.emit(name)

    def setLevels(self, levels, reset=True):
        """
        Change the level of set of loggers.

        Arguments:
            reset: If true, unspecified logger levels are reset to 0 (`NOTSET`)
        """
        if reset:
            names = list(logging.Logger.manager.loggerDict.keys())
            names.append(None)
        else:
            names = levels.keys()
        for name in names:
            logger = logging.getLogger(name)
            level = levels.get(name, logging.NOTSET)
            logger.setLevel(level)
        self.levelsConfigHaveChanged.emit()
