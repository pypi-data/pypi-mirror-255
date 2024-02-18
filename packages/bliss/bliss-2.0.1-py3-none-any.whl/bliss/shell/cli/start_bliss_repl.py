# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

import logging
import sys

# Do not import any more stuffs here to avoid warnings on stdout
# See bellow after early_logging_startup

from .. import log_utils

log_utils.early_logging_startup()

expert_error_report = sys.argv[4] == "1" if len(sys.argv) > 4 else False

with log_utils.filter_import_warnings(
    ignore_warnings=not expert_error_report
) as early_log_info:
    from .repl import embed
    from bliss import current_session
    from bliss import global_map


def main(global_map=global_map):
    session_name = sys.argv[1]

    # initialize logging
    log_level = getattr(logging, sys.argv[2].upper())
    log_utils.logging_startup(log_level)

    try:
        embed(
            session_name=session_name,
            use_tmux=True,
            style=sys.argv[3],
            expert_error_report=expert_error_report,
            early_log_info=early_log_info,
        )
    finally:
        try:
            current_session.close()
        except AttributeError:
            # no current session
            pass
        global_map.clear()


if __name__ == "__main__":
    main()
