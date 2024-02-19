from typing import override

from dearpygui import dearpygui as dpg
from keyboard import add_hotkey

from trainerbase.common.teleport import Teleport
from trainerbase.gui.helpers import add_components
from trainerbase.gui.objects import GameObjectUI
from trainerbase.gui.types import AbstractUIComponent
from trainerbase.tts import say


class TeleportUI(AbstractUIComponent):
    DPG_TAG_TELEPORT_LABELS = "__teleport_labels"

    def __init__(
        self,
        tp: Teleport,
        hotkey_save_position: str | None = "Insert",
        hotkey_set_saved_position: str | None = "Home",
        hotkey_dash: str | None = "End",
        tts_on_hotkey: bool = True,
    ):
        self.tp = tp
        self.hotkey_save_position = hotkey_save_position
        self.hotkey_set_saved_position = hotkey_set_saved_position
        self.hotkey_dash = hotkey_dash
        self.tts_on_hotkey = tts_on_hotkey

    @override
    def add_to_ui(self) -> None:
        self._tp_add_save_set_position_hotkeys_if_needed()
        self._tp_add_dash_hotkeys_if_needed()

        add_components(
            GameObjectUI(self.tp.player_x, "X"),
            GameObjectUI(self.tp.player_y, "Y"),
            GameObjectUI(self.tp.player_z, "Z"),
        )

        self._tp_add_labels_if_needed()

        dpg.add_button(label="Clip Coords", callback=self.on_clip_coords)

    def on_clip_coords(self):
        dpg.set_clipboard_text(repr(self.tp.get_coords()))

    def on_hotkey_save_position_press(self):
        self.tp.save_position()

        if self.tts_on_hotkey:
            say("Position saved")

    def on_hotkey_set_saved_position_press(self):
        is_position_restored = self.tp.restore_saved_position()

        if self.tts_on_hotkey:
            say("Position restored" if is_position_restored else "Save position at first")

    def on_hotkey_dash_press(self):
        self.tp.dash()
        if self.tts_on_hotkey:
            say("Dash!")

    def on_goto_label(self):
        self.tp.goto(dpg.get_value(self.DPG_TAG_TELEPORT_LABELS))

    def _tp_add_save_set_position_hotkeys_if_needed(self):
        if self.hotkey_save_position is None or self.hotkey_set_saved_position is None:
            return

        add_hotkey(self.hotkey_save_position, self.on_hotkey_save_position_press)
        add_hotkey(self.hotkey_set_saved_position, self.on_hotkey_set_saved_position_press)

        dpg.add_text(f"[{self.hotkey_save_position}] Save Position")
        dpg.add_text(f"[{self.hotkey_set_saved_position}] Restore Position")

    def _tp_add_dash_hotkeys_if_needed(self):
        if self.hotkey_dash is None:
            return

        add_hotkey(self.hotkey_dash, self.on_hotkey_dash_press)

        dpg.add_text(f"[{self.hotkey_dash}] Dash")

    def _tp_add_labels_if_needed(self):
        if not self.tp.labels:
            return

        labels = sorted(self.tp.labels.keys())

        with dpg.group(horizontal=True):
            dpg.add_button(label="Go To", callback=self.on_goto_label)
            dpg.add_combo(label="Labels", tag=self.DPG_TAG_TELEPORT_LABELS, items=labels, default_value=labels[0])
