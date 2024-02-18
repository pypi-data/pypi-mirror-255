# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
"""
Helper to display a refreshable block of text.
"""

from __future__ import annotations
from typing import Callable

import logging
import gevent
import greenlet

from prompt_toolkit.key_binding.key_bindings import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.filters import is_done
from prompt_toolkit.application import Application
from prompt_toolkit.layout import ConditionalContainer
from prompt_toolkit.filters import Condition
from bliss.common.greenlet_utils import asyncio_gevent
from prompt_toolkit.layout import (
    FormattedTextControl,
    HSplit,
    Layout,
    Window,
)
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit import ANSI, HTML


_logger = logging.getLogger(__name__)


class _TextBlockKeyboardInterrupt(RuntimeError):
    """This exception is used as a work around to close the prompt.

    It sounds like gevent-asyncio is not properly handling the raise of such
    base exception in this context.
    """


class _TextBlockKeyboardInterruptGeventExit(gevent.GreenletExit):
    """This exception is used as a work around to close the prompt.

    It sounds like gevent-asyncio is not properly handling the raise of such
    base exception in this context.

    It inherite from `GreenletExit` to make sure it is not logged by gevent.
    """


class TextBlockApplication(Application):
    """Handle a refreshable text block.

    A user function (`render`) have to be defined to render the block content.
    It have to return the height of the block and the text content. The height
    can change dynalically, and the text can be one of `str` or prompt toolkit
    formatting classes `HTML`, `ANSI`, `FormattedText`.

    A `process` function can be defined, to process in a background stuffs,
    like moving motors. It can be one of a callable or a greenlet. If this
    function is defined, the application will terminated just after the
    termination of this processing function.

    The application can be aborted by the user with CTRL-C. If a `process`
    function was defined, it is first killed, then the application terminate
    by raising a `KeyboardInterrupt` exception.

    Here is a base code with only a renderer function:

    .. code-block:: python

        def render():
            # User function which returns height and content
            import time
            return 1, f"time.time()"

        app = TextBlockApplication(
            render=render,
            refresh_interval=0.3,
        )
        app.exec()

    Here is a base code with a background processing:

    .. code-block:: python

        def background():
            # Do some stuffs
            gevent.sleep(10.0)

        def render():
            import time
            return 1, f"{time.time()}"

        app = TextBlockApplication(
            render=render,
            refresh_interval=0.3,
        )
        app.exec(process=background)
    """

    def __init__(
        self,
        render: Callable[[], tuple[int, str | FormattedText]],
        refresh_interval=0.3,
        style: Style | None = None,
    ):
        self._render: Callable[[], tuple[int, str | FormattedText]] = render
        self._window_height: int
        self._handled_greenlet: gevent.Greenlet | None = None
        self._window_height, _ = self._render()
        self._interruption_requested: bool = False
        self._initialized: gevent.event.Event = gevent.event.Event()
        self._was_render = gevent.event.Event()

        content = Window(
            FormattedTextControl(self._get_text),
            height=self._get_height,
            style="class:shell-move",
        )

        bottom_toolbar = ConditionalContainer(
            Window(
                FormattedTextControl(
                    " [ctrl-c] Abort", style="class:bottom-toolbar.text"
                ),
                style="class:bottom-toolbar",
                height=1,
            ),
            filter=Condition(lambda: not is_done() and not self.interruption_requested),
        )

        abort_toolbar = ConditionalContainer(
            Window(
                FormattedTextControl(
                    " Aborting... Please wait", style="class:bottom-toolbar.text"
                ),
                style="class:bottom-toolbar class:aborting",
                height=1,
            ),
            filter=Condition(lambda: not is_done() and self.interruption_requested),
        )

        Application.__init__(
            self,
            min_redraw_interval=0.05,
            refresh_interval=refresh_interval,
            layout=Layout(
                HSplit(
                    [
                        content,
                        Window(height=1),
                        bottom_toolbar,
                        abort_toolbar,
                    ]
                )
            ),
            mouse_support=False,
            key_bindings=self._create_bindings(),
            style=style,
        )

    def wait_render(self, timeout=None) -> bool:
        """Wait until the first render"""
        return self._was_render.wait(timeout=timeout)

    def _redraw(self, render_as_done: bool = False) -> None:
        # Overrided to capture the render signal
        try:
            return Application._redraw(self, render_as_done=render_as_done)
        finally:
            self._was_render.set()

    @property
    def interruption_requested(self) -> bool:
        """True if ctrl-c was pressed to request interruption"""
        return self._interruption_requested

    def _get_height(self) -> int:
        return self._window_height

    def _get_text(self) -> str | FormattedText | ANSI | HTML:
        try:
            self._window_height, line = self._render()
        except Exception as e:
            # Robustness if the user rendering fails
            self._window_height = 0
            self.exit(exception=e, style="class:exiting")
            if self._handled_greenlet:
                # This will block the UI but it is not much important
                # Because such problem have to be fixed first in the user function
                self._handled_greenlet.kill()
            return ""
        return line

    def _create_bindings(self) -> KeyBindings:
        """
        Create the KeyBindings for a prompt application.
        """
        kbind = KeyBindings()

        @kbind.add("c-c")
        def _keyboard_interrupt(event: KeyPressEvent) -> None:
            "Abort when Control-C has been pressed."
            if self._handled_greenlet is None or self._handled_greenlet.ready():
                if not event.app.is_done:
                    # Make sure `self.exit` will be properly executed
                    self._initialized.wait()
                    event.app.exit(
                        exception=_TextBlockKeyboardInterrupt, style="class:aborting"
                    )
            else:
                self._interruption_requested = True
                self.invalidate()
                self._handled_greenlet.kill(
                    _TextBlockKeyboardInterruptGeventExit, block=False
                )

        return kbind

    def _when_initialization_done(self):
        """Called when the application was properly initialized"""
        self._initialized.set()

    def _handled_greenlet_terminated(self, greenlet: greenlet.Greenlet):
        """Called when the handled greenlet was terminated"""
        # Make sure `self.exit` will be properly executed
        self._initialized.wait()
        if not self.is_done:
            if self._interruption_requested:
                self.exit(exception=_TextBlockKeyboardInterrupt)
            else:
                self.exit()

    def exec(self, process: gevent.Greenlet | Callable | None = None, *args, **kwargs):
        """
        Execute the application.

        Argument:
            process: If defined, the application will handle a processing.
                     This can be a greenlet or a callable (which will be
                     spawned with gevent).

        Raises:
            KeyboardInterrupt: If the application was aborted with ctrl-c
        """
        self._initialized.clear()
        self._was_render.clear()
        if process is None:
            self._handled_greenlet = None
        elif isinstance(process, gevent.Greenlet):
            if process.ready():
                return
            self._handled_greenlet = process
        elif callable(process):
            self._handled_greenlet = gevent.spawn(process, *args, **kwargs)
        else:
            raise TypeError(f"Type of 'process' {type(process)} unsupported")

        if self._handled_greenlet is not None:
            self._handled_greenlet.link(self._handled_greenlet_terminated)

        try:
            asyncio_gevent.yield_future(
                self.run_async(
                    pre_run=self._when_initialization_done, handle_sigint=False
                )
            )
        except _TextBlockKeyboardInterrupt:
            if self._handled_greenlet is not None:
                # This does not raise exception when it was killed
                self._handled_greenlet.get()
                self._handled_greenlet = None
            raise KeyboardInterrupt
        except gevent.GreenletExit:
            # The application was in a greenlet and was interrupted
            # We have to deal with the handled greenlet
            if self._handled_greenlet is not None:
                self._handled_greenlet.kill()
            self._handled_greenlet.join()
            raise
        else:
            if self._handled_greenlet is not None:
                try:
                    self._handled_greenlet.get()
                    self._handled_greenlet = None
                except _TextBlockKeyboardInterruptGeventExit:
                    raise KeyboardInterrupt
        finally:
            # Allow to flush the unitests with the termination of the application
            # See SimulatedOutput
            output = self.output
            if hasattr(output, "_flush_app"):
                output._flush_app()
