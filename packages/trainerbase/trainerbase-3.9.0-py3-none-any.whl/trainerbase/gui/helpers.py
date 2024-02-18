from collections.abc import Callable
from functools import wraps

from dearpygui import dearpygui as dpg

from trainerbase.gui.types import AbstractUIComponent


def add_components(*components: AbstractUIComponent):
    for component in components:
        component.add_to_ui()


def simple_trainerbase_menu(window_title: str, width: int, height: int):
    def menu_decorator(initializer: Callable):
        @wraps(initializer)
        def run_menu_wrapper(on_initialized: Callable):
            dpg.create_context()
            dpg.create_viewport(
                title=window_title,
                min_width=width,
                min_height=height,
                width=width,
                height=height,
            )
            dpg.setup_dearpygui()

            with dpg.window(
                label=window_title,
                tag="menu",
                min_size=[width, height],
                no_close=True,
                no_move=True,
                no_title_bar=True,
                horizontal_scrollbar=True,
            ):
                initializer()

            dpg.show_viewport()

            on_initialized()

            dpg.start_dearpygui()
            dpg.destroy_context()

        return run_menu_wrapper

    return menu_decorator
