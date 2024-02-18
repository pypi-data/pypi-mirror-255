from abc import ABC, abstractmethod
from typing import Self, override

from pymem.exception import MemoryWriteError

from trainerbase.common.abc import Switchable
from trainerbase.memory import ConvertibleToAddress, ensure_address, pm


class AbstractReadableObject[T](ABC):
    @property
    @abstractmethod
    def value(self) -> T:
        pass


class GameObject[PymemType, TrainerBaseType](AbstractReadableObject[TrainerBaseType]):
    tracked_objects: list[Self] = []
    value_range: None | tuple[TrainerBaseType, TrainerBaseType] = None

    @staticmethod
    @abstractmethod
    def pm_read(address: int) -> PymemType:
        pass

    @staticmethod
    @abstractmethod
    def pm_write(address: int, value: PymemType) -> None:
        pass

    def __init__(
        self,
        address: ConvertibleToAddress,
        frozen: TrainerBaseType | None = None,
        is_tracked: bool = True,
        value_range: None | tuple[TrainerBaseType, TrainerBaseType] = None,
    ):
        if is_tracked:
            GameObject.tracked_objects.append(self)

        self.address = ensure_address(address)
        self.frozen = frozen
        self.is_tracked = is_tracked

        if value_range is not None:
            self.value_range = value_range

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}"
            f" at {hex(self.address.resolve())}:"
            f" value={self.value},"
            f" frozen={self.frozen}"
            ">"
        )

    def after_read(self, value: PymemType) -> TrainerBaseType:
        return value  # type: ignore

    def before_write(self, value: TrainerBaseType) -> PymemType:
        return value  # type: ignore

    def validate_range(self, value: TrainerBaseType) -> bool:
        if self.value_range is None:
            return True

        if not isinstance(value, (int, float)):
            raise TypeError(f"Unable to validate range for non-numeric value: {value} (type: {type(value)})")

        min_value, max_value = self.value_range

        return min_value <= value <= max_value  # type: ignore

    @property
    @override
    def value(self) -> TrainerBaseType:
        return self.after_read(self.pm_read(self.address.resolve()))

    @value.setter
    def value(self, new_value: TrainerBaseType):
        if not self.validate_range(new_value):
            raise ValueError(f"Wrong value for type {type(self)}: {new_value} not in range {self.value_range}")

        self.pm_write(self.address.resolve(), self.before_write(new_value))


class GameFloat(GameObject[float, float]):
    value_range: tuple[float, float] = (-3.4e38, 3.4e38)
    pm_read = pm.read_float  # type: ignore
    pm_write = pm.write_float

    @override
    def before_write(self, value):
        return float(value)


class GameDouble(GameObject[float, float]):
    value_range: tuple[float, float] = (-1.7e308, 1.7e308)
    pm_read = pm.read_double  # type: ignore
    pm_write = pm.write_double

    @override
    def before_write(self, value):
        return float(value)


class GameByte(GameObject[bytes, int]):
    value_range: tuple[int, int] = (0, 255)

    @staticmethod
    @override
    def pm_read(address: int) -> bytes:
        return pm.read_bytes(address, length=1)

    @staticmethod
    @override
    def pm_write(address: int, value: bytes) -> None:
        pm.write_bytes(address, value, length=1)

    @override
    def before_write(self, value: int) -> bytes:
        return value.to_bytes(length=1, byteorder="little")

    @override
    def after_read(self, value: bytes) -> int:
        return int.from_bytes(value, byteorder="little")


class GameInt(GameObject[int, int]):
    value_range: tuple[int, int] = (-2_147_483_648, 2_147_483_647)

    pm_read = pm.read_int  # type: ignore
    pm_write = pm.write_int


class GameShort(GameObject[int, int]):
    value_range: tuple[int, int] = (-32_768, 32_767)

    pm_read = pm.read_short  # type: ignore
    pm_write = pm.write_short


class GameLongLong(GameObject[int, int]):
    value_range: tuple[int, int] = (-(2**63), (2**63) - 1)

    pm_read = pm.read_longlong  # type: ignore
    pm_write = pm.write_longlong


class GameUnsignedInt(GameObject[int, int]):
    value_range: tuple[int, int] = (0, 4_294_967_295)

    pm_read = pm.read_uint  # type: ignore
    pm_write = pm.write_uint


class GameUnsignedShort(GameObject[int, int]):
    value_range: tuple[int, int] = (0, 65_535)

    pm_read = pm.read_ushort  # type: ignore
    pm_write = pm.write_ushort


class GameUnsignedLongLong(GameObject[int, int]):
    value_range: tuple[int, int] = (0, 18_446_744_073_709_551_615)

    pm_read = pm.read_ulonglong  # type: ignore
    pm_write = pm.write_ulonglong


class GameBool(GameObject[bool, bool], Switchable):
    value_range: tuple[bool, bool] = (False, True)

    pm_read = pm.read_bool  # type: ignore
    pm_write = pm.write_bool

    @override
    def enable(self):
        self.value = True  # pylint: disable=attribute-defined-outside-init

    @override
    def disable(self):
        self.value = False  # pylint: disable=attribute-defined-outside-init


class ReadonlyGameObjectSumGetter(AbstractReadableObject[int | float]):
    def __init__(self, *game_numbers: GameInt | GameFloat):
        self.game_numbers = game_numbers

    @property
    def value(self) -> int | float:
        return sum(number.value for number in self.game_numbers)


def update_frozen_objects():
    for game_object in GameObject.tracked_objects:
        if game_object.frozen is not None:
            try:
                game_object.value = game_object.frozen
            except (MemoryWriteError, ValueError):
                continue
