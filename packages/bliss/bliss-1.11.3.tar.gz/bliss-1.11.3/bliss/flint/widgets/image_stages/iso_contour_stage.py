# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import os
import numpy
import logging
import typing
from silx.gui import qt
from silx.gui.dialog.ImageFileDialog import ImageFileDialog
from .base_stage import BaseStage


_logger = logging.getLogger(__name__)


class IsoContourStage(BaseStage):
    def __init__(self, parent: qt.QObject = None):
        BaseStage.__init__(self, parent=parent)
        self.__value = 20
        self.__isocontour = None

    def requestMaskFile(self):
        """Request user to load a mask"""
        dialog = ImageFileDialog(self._findRelatedWidget())
        if self.__maskDir is not None and os.path.exists(self.__maskDir):
            dialog.setDirectory(self.__maskDir)

        result = dialog.exec_()
        if not result:
            return
        try:
            mask = dialog.selectedImage()
            if mask is not None:
                self.setMask(mask)
        except Exception:
            _logger.error("Error while loading a mask", exc_info=True)
        self.__maskDir = dialog.directory()

    def setValue(self, value):
        """Set the actual value"""
        self.__value = value
        self.configUpdated.emit()

    def value(self):
        """Returns the value used to filter the image"""
        return self.__value

    def isValid(self):
        return True

    def isoContours(self):
        return self.__isocontour

    def correction(self, image: numpy.ndarray, mask: typing.Optional[numpy.ndarray]):
        self._resetApplyedCorrections()
        try:
            from silx.image.marchingsquares import MarchingSquaresMergeImpl

            algo = MarchingSquaresMergeImpl(image, mask)
            polygons = algo.find_contours(self.__value)
            self.__isocontour = polygons
        except Exception:
            _logger.error("Error while computing isocontour", exc_info=True)
            self.__isocontour = None

        return None
