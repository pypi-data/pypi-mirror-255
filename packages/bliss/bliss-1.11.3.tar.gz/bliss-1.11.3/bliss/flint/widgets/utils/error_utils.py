# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import contextlib
import logging
from silx.gui import qt

_logger = logging.getLogger(__name__)


@contextlib.contextmanager
def exceptionAsMessageBox(parent: qt.QWidget):
    try:
        yield
    except Exception as e:
        _logger.warning("Error catched by an message box", exc_info=True)
        try:
            msg = str(e.args[0])
        except Exception:
            msg = str(e)
        qt.QMessageBox.critical(parent, "Error", msg)
