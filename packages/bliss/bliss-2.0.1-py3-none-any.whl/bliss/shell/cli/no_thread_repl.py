# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""PtPython REPL with no threads"""
import asyncio
import functools
import traceback
from bliss.common.greenlet_utils import asyncio_gevent
import gevent
from typing import Optional
from ptpython.repl import PythonRepl, set_title, clear_title
from ptpython.python_input import (
    AutoSuggestFromHistory,
    Buffer,
    ConditionalValidator,
    ConditionalAutoSuggest,
    Condition,
    DEFAULT_BUFFER,
    Document,
    InputMode,
    unindent_code,
)


class NoThreadPythonRepl(PythonRepl):
    """
    ptpython PythonRepl with no threads

    Threads have been introduced in ptpython 3.0.11 ; the input UI runs in a
    separate thread. In addition, default completers also run in threads.
    This is a problem for us, for 3 reasons:

    - aiogevent sets up a gevent backend for asyncio, as a result operations that
      run in an executor for example are executing in different gevent hubs ; it
      is not safe to share gevent objects between threads
    - when showing results, code is called from another thread
        - as we display `__info__` strings which can communicate via sockets etc,
        we get "cannot switch to a different thread" error since sockets cannot be
        shared between gevent loops in different threads
    - when executing properties and methods discovery for completion, there is a
      possibility of communication via sockets, to get redis keys (for example),
      this cannot be executed in another thread (same reason as above)

    This code overwrites ._create_buffer(), .read() and .run_async() in order to provide
    versions with no threads ; in our case there is no blocking because we use
    aiogevent for asyncio + monkey-patched Python so we can avoid threads
    completely.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._current_eval_g = None  # greenlet of the command being executed in shell

    def _create_buffer(self) -> Buffer:
        """
        Create the `Buffer` for the Python input.

        Same method as super()._create_buffer, except that completers and auto-suggestion are
        replaced by non-threaded flavours
        """
        # only completers are changed to non-threaded flavours
        python_buffer = Buffer(
            name=DEFAULT_BUFFER,
            complete_while_typing=Condition(lambda: self.complete_while_typing),
            enable_history_search=Condition(lambda: self.enable_history_search),
            tempfile_suffix=".py",
            history=self.history,
            completer=self._completer,  # was: ThreadedCompleter(self._completer)
            validator=ConditionalValidator(
                self._validator, Condition(lambda: self.enable_input_validation)
            ),
            auto_suggest=ConditionalAutoSuggest(
                AutoSuggestFromHistory(),  # was: ThreadedAutoSuggest(AutoSuggestFromHistory())
                Condition(lambda: self.enable_auto_suggest),
            ),
            accept_handler=self._accept_handler,
            on_text_changed=self._on_input_timeout,
        )

        return python_buffer

    async def read(self) -> str:
        """Read the input

        Same method as super().read, except that thread is replaced by asyncio
        (hence the 'async' keyword added to method definition)
        """
        # Capture the current input_mode in order to restore it after reset,
        # for ViState.reset() sets it to InputMode.INSERT unconditionally and
        # doesn't accept any arguments.
        def pre_run(
            last_input_mode: InputMode = self.app.vi_state.input_mode,
        ) -> None:
            if self.vi_keep_last_used_mode:
                self.app.vi_state.input_mode = last_input_mode

            if not self.vi_keep_last_used_mode and self.vi_start_in_navigation_mode:
                self.app.vi_state.input_mode = InputMode.NAVIGATION

        # Run the UI.
        result: str = ""
        exception: Optional[BaseException] = None

        async def in_thread() -> None:
            nonlocal result, exception
            try:
                while True:
                    try:
                        result = await self.app.run_async(pre_run=pre_run)
                        if result is None:
                            result = ""

                        if result.lstrip().startswith("\x1a"):
                            # When the input starts with Ctrl-Z, quit the REPL.
                            # (Important for Windows users.)
                            raise EOFError

                        # Remove leading whitespace.
                        # (Users can add extra indentation, which happens for
                        # instance because of copy/pasting code.)
                        result = unindent_code(result)

                        if result and not result.isspace():
                            return
                    except KeyboardInterrupt:
                        # Abort - try again.
                        self.default_buffer.document = Document()
                    except BaseException as e:
                        exception = e
                        return

            finally:
                if self.insert_blank_line_after_input:
                    self.app.output.write("\n")

        await in_thread()  # was: threading.Thread(target=in_thread); thread.start(); thread.join()

        if exception is not None:
            raise exception
        return result

    def kill_current_eval(self):
        """Kill the currently running command, by raising a KeyboardInterrupt.
        KeyboardInterrupt cannot raises outside that greenlet, instead it is
        converted to gevent.GreenletExit to keep the eval loop running.

        This function can be used in signal handlers to abort commands."""

        # ---- CRITICAL SECTION ---------------------------------------------- #
        # atomic because of gevent cooperative multitasking
        if self._current_eval_g._can_be_killed:
            self._current_eval_g.kill(KeyboardInterrupt, block=False)
        # -------------------------------------------------------------------- #

    def eval_greenlet(self, text):
        """Return a non started greenlet. This allows for the greenlet to be
        wrapped into an asyncio future before it starts."""
        eval_g = gevent.Greenlet(self.eval, text)
        eval_g._can_be_killed = False

        def keyboard_interrupt_shield(func):
            @functools.wraps(func)
            def f(*args, **kwargs):
                # ---- CRITICAL SECTION -------------------------------------- #
                # DO NOT INTRODUCE A BLOCKING CALL IN THIS SECTION.
                # When calling greenlet.start(), the greenlet is scheduled but
                # not executing yet. From that moment it can be killed, which
                # let it no time to protect in a try/except block.
                # Here we prevent the greenlet to be killed before entering
                # try/except. Use self.kill_current_eval() only (not kill()
                # directly).
                try:
                    eval_g._can_be_killed = True
                    # -------------------------------------------------------- #

                    return func(*args, **kwargs)

                # ---- CRITICAL SECTION -------------------------------------- #
                # DO NOT INTRODUCE A BLOCKING CALL IN THIS SECTION.
                # When an exception is raised, the greenlet won't let another
                # greenlet to execute (including SIGINT handler) until flag is
                # unset.
                except KeyboardInterrupt as e:
                    # KeyboardInterrupt is normally handled by the current eval
                    # greenlet. But one could occur during error handling
                    # itself, in that case it is transformed into an harmless
                    # exception to not propagate higher.
                    raise gevent.GreenletExit from e
                finally:
                    eval_g._can_be_killed = False
                # ------------------------------------------------------------ #

            return f

        eval_g._run = keyboard_interrupt_shield(eval_g._run)
        return eval_g

    async def run_async(self) -> None:
        """Run the REPL loop

        This is inspired by super().run_async, except that there is no thread
        and "eval" is not started in a future it just relies on gevent
        """
        if self.terminal_title:
            set_title(self.terminal_title)

        self._add_to_namespace()

        try:
            while True:
                # Read.
                try:
                    text = (
                        await self.read()
                    )  # was: await loop.run_in_executor(None, self.read)

                    # prepare greenlet and its wrapper future (not started yet)
                    self._current_eval_g = self.eval_greenlet(text)
                    future = asyncio_gevent.greenlet_to_future(self._current_eval_g)

                    # Eval.
                    try:
                        # greenlet can be started once properly wrapped in future
                        self._current_eval_g.start()
                        try:
                            await future
                        except asyncio.exceptions.CancelledError:
                            # If only the future is cancelled, then gevent.get
                            # will catch it for display. If quit() builtin is
                            # called, then gevent.get will get a SystemExit.
                            pass
                        result = self._current_eval_g.get()
                    except SystemExit:
                        # do not catch the SystemExit from quit() command
                        raise
                    except BaseException:
                        # An Exception occured outside of the evaluated command,
                        # dump the bare traceback.
                        print(traceback.format_exc())
                        result = None

                    if isinstance(result, gevent.GreenletExit):
                        # When the greenlet get a KeyboardInterrupt outside of
                        # normal error handling section. It bubbles up to asyncio_gevent
                        # which convert it to GreenletExit. Which ends up there.
                        result = None

                    # Print.
                    if result is not None:
                        self.show_result(
                            result
                        )  # was: await loop.run_in_executor(None, lambda: self.show_result(result))

                    # Loop.
                    self.current_statement_index += 1
                    self.signatures = []
                except EOFError:
                    return
                except SystemExit:
                    return
        finally:
            if self.terminal_title:
                clear_title()
            self._remove_from_namespace()
