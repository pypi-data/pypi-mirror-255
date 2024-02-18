# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Patch to modify the behavior of the ptpython PythonCompleter
The code for def signature_toolbar corresponds to ptpython version 2.0.4
"""
import ptpython.completer
from importlib.metadata import version

if version("jedi") < "0.19":
    import jedi
    import collections
    from bliss.common.utils import autocomplete_property
else:
    jedi = None

old_get_completions = ptpython.completer.PythonCompleter.get_completions


def NEWget_completions(self, document, complete_event):
    """
    Get Python completions. Hide those starting with "_" (unless user first types the underscore).
    """
    allow_underscore = document.text.endswith("_") or document.text.rpartition(".")[
        -1
    ].startswith("_")

    try:

        if allow_underscore:
            yield from old_get_completions(self, document, complete_event)
        else:
            yield from (
                c
                for c in old_get_completions(self, document, complete_event)
                if not c.text.startswith("_")
            )

    except Exception:
        pass  # tmp fix see issue 2906 # https://gitlab.esrf.fr/bliss/bliss/-/merge_requests/3944


ptpython.completer.PythonCompleter.get_completions = NEWget_completions

if jedi is not None:
    jedi.api.Interpreter._allow_descriptor_getattr_default = False
    jedi.inference.compiled.access.ALLOWED_DESCRIPTOR_ACCESS += (
        autocomplete_property,
        collections._tuplegetter,
    )
