from pathlib import Path
from typing import Final, Self

from pyinjector import inject
from pymem.exception import MemoryWriteError
from pymem.process import module_from_name

from trainerbase.gameobject import GameDouble
from trainerbase.memory import ARCH, pm


SPEEDHACK_DLL_MODULE_NAME: Final[str] = f"speedhack{ARCH}.dll"
SPEEDHACK_DLL_PATH: Final[Path] = (
    Path(__file__).resolve().parent.parent / "trainerbase_vendor" / SPEEDHACK_DLL_MODULE_NAME
)
SPEED_MODIFIER_OFFSET: Final[int] = 0x40058 if ARCH == 32 else 0x47098


class SpeedHack:
    _instance: Self | None = None

    def __new__(cls, *_args, **_kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        self._dll_injection_address = self._inject()
        self._speed_modifier = GameDouble(self._dll_injection_address + SPEED_MODIFIER_OFFSET)

        self.factor = 1.0

    def _inject(self) -> int:
        inject(pm.process_id, str(SPEEDHACK_DLL_PATH))  # type: ignore

        speedhack32_address = module_from_name(pm.process_handle, SPEEDHACK_DLL_MODULE_NAME).lpBaseOfDll  # type: ignore

        return speedhack32_address

    @property
    def factor(self):
        return self._speed_modifier.value

    @factor.setter
    def factor(self, value: float):
        self._speed_modifier.value = value

    @classmethod
    def disable(cls):
        if cls._instance is None:
            return

        # TODO: Should I eject dll?
        try:
            cls._instance.factor = 1.0
        except MemoryWriteError:
            pass
