# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2022 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import numpy
import typing
import logging
from silx.gui import qt
from .info import ImageCorrections
from .base_stage import BaseStage


_logger = logging.getLogger(__name__)


class ExposureTimeStage(BaseStage):
    def __init__(self, parent: qt.QObject = None):
        BaseStage.__init__(self, parent=parent)

    def correction(self, array: numpy.ndarray, exposureTime: typing.Optional[float]):
        self._resetApplyedCorrections()
        if exposureTime is not None:
            array = array / exposureTime
            self._setApplyedCorrections([ImageCorrections.EXPOTIME_CORRECTION])
        return array
