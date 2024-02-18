# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.

"""
Functions suite to prompt for various user inputs in shell.
"""

from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit import PromptSession
from prompt_toolkit.application.current import get_app
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.shortcuts.prompt import CompleteStyle
from prompt_toolkit.filters import (
    Condition,
    has_focus,
    is_true,
    to_filter,
)
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.key_binding.bindings.completion import (
    display_completions_like_readline,
)
from prompt_toolkit.key_binding.key_bindings import (
    KeyBindings,
)
from prompt_toolkit.utils import (
    suspend_to_background_supported,
)
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit import print_formatted_text

from bliss.common.greenlet_utils import asyncio_gevent
from bliss.common.utils import Undefined
from bliss.shell.standard import clear


STYLE = None
"""This can be overwritten to tune the formatting"""


_DEFAULT_STYLE = Style.from_dict(
    {
        "question": "bold",
        "valid_input": "",
        "prompt_char": "",
        "separator": "",
        "description": "",
        "title": "yellow bold",
        "subtitle": "bold",
    }
)


def get_style():
    global STYLE, _DEFAULT_STYLE
    return STYLE or _DEFAULT_STYLE


class _GetvalKeyboardInterrupt(RuntimeError):
    """This exception is used as a work around to close the prompt.

    It sounds like gevent-asyncio is not properly handling the raise of such
    base exception in this context.
    """


class BlissPromptSession(PromptSession):
    """Override PromptSession only to raise _GetvalKeyboardInterrupt on a
    keyboard interrupt"""

    def _create_prompt_bindings(self) -> KeyBindings:
        """
        Create the KeyBindings for a prompt application.
        """
        kbind = KeyBindings()
        handle = kbind.add
        default_focused = has_focus(DEFAULT_BUFFER)

        @Condition
        def do_accept() -> bool:
            return not is_true(self.multiline) and self.app.layout.has_focus(
                DEFAULT_BUFFER
            )

        @handle("enter", filter=do_accept & default_focused)
        def _accept_input(event: KeyPressEvent) -> None:
            "Accept input when enter has been pressed."
            self.default_buffer.validate_and_handle()

        @Condition
        def readline_complete_style() -> bool:
            return self.complete_style == CompleteStyle.READLINE_LIKE

        @handle("tab", filter=readline_complete_style & default_focused)
        def _complete_like_readline(event: KeyPressEvent) -> None:
            "Display completions (like Readline)."
            display_completions_like_readline(event)

        @handle("c-c", filter=default_focused)
        def _keyboard_interrupt(event: KeyPressEvent) -> None:
            "Abort when Control-C has been pressed."
            event.app.exit(exception=_GetvalKeyboardInterrupt, style="class:aborting")

        @Condition
        def ctrl_d_condition() -> bool:
            """Ctrl-D binding is only active when the default buffer is selected
            and empty."""
            app = get_app()
            return (
                app.current_buffer.name == DEFAULT_BUFFER
                and not app.current_buffer.text
            )

        @handle("c-d", filter=ctrl_d_condition & default_focused)
        def _eof(event: KeyPressEvent) -> None:
            "Exit when Control-D has been pressed."
            event.app.exit(exception=EOFError, style="class:exiting")

        suspend_supported = Condition(suspend_to_background_supported)

        @Condition
        def enable_suspend() -> bool:
            return to_filter(self.enable_suspend)()

        @handle("c-z", filter=suspend_supported & enable_suspend)
        def _suspend(event: KeyPressEvent) -> None:
            """
            Suspend process to background.
            """
            event.app.suspend_to_background()

        return kbind


def _prompt_factory():
    return BlissPromptSession()


def _ki_default_argument(func):
    """Function decorator to return a default value when keyboard interrupt
    is pressed.

    The function use a new parameter `ki_default`. If defined, this value is
    returned if the initial function was interrupted wuth `KeyboardInterrupt`.
    """

    def newfunc(*args, ki_default=Undefined, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            if ki_default is not Undefined:
                return ki_default
            raise

    newfunc.__doc__ = func.__doc__
    return newfunc


def _clear_screen_argument(func):
    """Function decorator to optionally clear the screen before the real function.

    The function use a new parameter `clear_screen`. If true, the screen is
    cleared. Default does not clear the screen.
    """

    def newfunc(*args, clear_screen=False, **kwargs):
        if clear_screen:
            clear()
        return func(*args, **kwargs)

    newfunc.__doc__ = func.__doc__
    return newfunc


def bliss_prompt(message, validator=None):
    """
    Default ptpython prompt embedded inside a thread to make it work with BLISS.
    """
    session = _prompt_factory()
    try:
        return asyncio_gevent.yield_future(
            session.prompt_async(
                message,
                validator=validator,
                handle_sigint=False,
                style=get_style(),
            )
        )
    except _GetvalKeyboardInterrupt:
        raise KeyboardInterrupt


def title(message):
    """Print a title in the shell"""
    print_formatted_text(
        FormattedText([("class:title", "\n" + message)]), style=get_style()
    )


def subtitle(message):
    """Print a title in the shell"""
    print_formatted_text(
        FormattedText([("class:subtitle", "\n" + message)]), style=get_style()
    )


@_clear_screen_argument
@_ki_default_argument
def getval_yes_no(message, default=None):
    """
    Prompt user with <message>, wait for a Y/N answer.

    If no default is specified, the function is blocking until the input is valid.

    Return:
        bool: True for yes, Y, Yes, YES etc.
              False for no, N, No, NO etc.
    """

    class YesNoValidator(Validator):
        def validate(self, document):
            text = document.text.lower()
            if text == "" and default is not None:
                return
            if text in ["y", "n", "yes", "no"]:
                return
            raise ValidationError(message="The input have to be on of [y]es or [n]o")

    if isinstance(default, str):
        if default.lower() in ["y", "yes"]:
            default = True
        elif default.lower() in ["n", "no"]:
            default = False
        else:
            raise ValueError(f"Invalid defautl value: {default}")

    if default is None:
        input_info = "[y/n]"
    elif default:
        input_info = "[Y/n]"
    else:
        input_info = "[y/N]"

    text = FormattedText(
        [
            ("class:question", message),
            ("", " "),
            ("class:valid_input", input_info),
            ("class:prompt_char", ": "),
        ]
    )

    user_choice = bliss_prompt(text, validator=YesNoValidator())
    if user_choice == "":
        return default
    return user_choice[0].lower() == "y"


@_clear_screen_argument
@_ki_default_argument
def getval_name(message, default=None):
    """
    Prompt user for a 'valid name', ie containing letters, numbers, and "_" chars only.
    ie: like a valid python identifier.
    NB: can be use to create (a part of) a file name.
    Return:
        str: user string if correct.
    """

    class NameValidator(Validator):
        def validate(self, document):
            text = document.text.lower()

            if text == "" and default is not None:
                # If there is a default, the empty value is valid
                return

            if not text.isidentifier():
                raise ValidationError(
                    message="The input must only contain 'a-z' 'A-Z' '0-9' and '_' characters"
                )

    if default is not None:
        default_text = f" [{default}]"
    else:
        default_text = ""

    text = FormattedText(
        [
            ("class:question", message),
            ("", " "),
            ("class:valid_input", default_text),
            ("class:prompt_char", ": "),
        ]
    )

    user_choice = bliss_prompt(text, validator=NameValidator())
    if user_choice == "":
        return default
    return user_choice


@_clear_screen_argument
@_ki_default_argument
def getval_int_range(message, minimum, maximum, default=None):
    """
    Prompt user for an int number in interval [minimum, maximum]

    Return:
        int: user value if correct.
    """

    class IntValidator(Validator):
        def validate(self, document):
            text = document.text.lower()
            if text == "" and default is not None:
                # If there is a default, the empty value is valid
                return
            try:
                value = int(text.strip())
            except ValueError as val_err:
                raise ValidationError(
                    message="The input is not a valid integer"
                ) from val_err

            if not (minimum <= value <= maximum):
                raise ValidationError(
                    message=f"The input is out of range [{minimum}..{maximum}]"
                )

    if default is not None:
        default_text = f" [{default}]"
    else:
        default_text = ""

    text = FormattedText(
        [
            ("class:question", message),
            ("", " "),
            ("class:valid_input", default_text),
            ("class:prompt_char", ": "),
        ]
    )

    user_choice = bliss_prompt(text, validator=IntValidator())
    if user_choice == "":
        return default
    return int(user_choice)


@_clear_screen_argument
@_ki_default_argument
def getval_idx_list(choices_list, message=None, default=None):
    """
    Return index and string chosen by user in list of N strings.
    Selection is done by index in [1..N].

    Parameters:
        choices_list: list of str
        message: str
    Returns: tuple(int, str)
        Selected index and string.
    """
    print_formatted_text("", style=get_style())
    if message is None:
        message = "Enter number of item:"

    def print_choice(choice, description):
        text = str(description).replace("\n", "\n    ")
        text = FormattedText(
            [
                ("class:valid_input", choice),
                ("class:separator", " - "),
                ("class:description", text),
            ]
        )
        print_formatted_text(text, style=get_style())

    for (index, value) in enumerate(choices_list):
        print_choice(str(index + 1), value)

    user_choice = getval_int_range(
        message, default=default, minimum=1, maximum=len(choices_list)
    )

    return (user_choice, choices_list[user_choice - 1])


@_clear_screen_argument
@_ki_default_argument
def getval_char_list(char_choice_list_or_dict, message=None, default=None):
    """
    Return character and string chosen by user in list of strings.
    Selection is done by letter provided by user.

    Parameters:
        char_choice_list_or_dict: list of tuples (str, str)  or dict
        message: str
    Returns: tuple(str, str)
        * str: single char selected by user
        * str: string selected by user
    """
    print_formatted_text("", style=get_style())

    choices_dict = dict()
    char_set = set()

    def print_choice(choice, description):
        text = str(description).replace("\n", "\n    ")
        text = FormattedText(
            [
                ("class:valid_input", choice),
                ("class:separator", " - "),
                ("class:description", text),
            ]
        )
        print_formatted_text(text, style=get_style())

    if isinstance(char_choice_list_or_dict, list):
        for (char, text) in char_choice_list_or_dict:
            choices_dict[char] = text
            char_set.add(char)
            print_choice(char, text)
    else:
        for (char, text) in char_choice_list_or_dict.items():
            choices_dict[char] = text
            char_set.add(char)
            print_choice(char, text)

    class CharValidator(Validator):
        def validate(self, document):
            text = document.text.lower()
            if text == "" and default is not None:
                # If there is a default, the empty value is valid
                return
            if text not in char_set:
                raise ValidationError(
                    message="The input does not refer to any available choice"
                )

    text = FormattedText(
        [
            ("class:question", message),
            ("class:prompt_char", ": "),
        ]
    )

    user_choice = bliss_prompt(text, validator=CharValidator())

    if user_choice == "":
        user_choice = default

    return (user_choice, choices_dict.get(user_choice))
