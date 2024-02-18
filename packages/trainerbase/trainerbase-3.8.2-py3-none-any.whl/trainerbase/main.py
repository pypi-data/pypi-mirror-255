from collections.abc import Callable
from functools import partial
from os import _exit as force_exit
from typing import NoReturn

from trainerbase.codeinjection import safely_eject_all_code_injections
from trainerbase.gameobject import update_frozen_objects
from trainerbase.gui import update_displayed_objects
from trainerbase.scriptengine import Script, system_script_engine
from trainerbase.speedhack import SpeedHack


def run(
    run_gui: Callable[[Callable], None],
    on_gui_initialized_hook: Callable | None = None,
    on_shutdown_hook: Callable | None = None,
) -> NoReturn:
    system_script_engine.register_script(Script(update_frozen_objects, enabled=True))
    system_script_engine.register_script(Script(update_displayed_objects, enabled=True))

    run_gui(partial(on_gui_initialized, on_gui_initialized_hook))

    system_script_engine.stop()
    safely_eject_all_code_injections()
    SpeedHack.disable()

    if on_shutdown_hook is not None:
        on_shutdown_hook()

    force_exit(0)


def on_gui_initialized(on_gui_initialized_hook: Callable | None = None):
    system_script_engine.start()

    if on_gui_initialized_hook is not None:
        on_gui_initialized_hook()
