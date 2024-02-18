from abc import ABC, abstractmethod
from pathlib import Path
from subprocess import DEVNULL
from subprocess import run as run_executable
from tempfile import TemporaryDirectory
from typing import Final, Never, Self, override

from pymem.exception import MemoryWriteError

from trainerbase.memory import ARCH, ConvertibleToAddress, ensure_address, pm


FASM_EXECUTABLE_PATH: Final[Path] = Path(__file__).resolve().parent.parent / "trainerbase_vendor" / "FASM.EXE"


type Code = bytes | str


class AbstractCodeInjection(ABC):
    created_code_injections: list[Self] = []

    def __new__(cls, *_args, **_kwargs):
        instance = super().__new__(cls)
        AbstractCodeInjection.created_code_injections.append(instance)

        return instance

    @abstractmethod
    def inject(self):
        pass

    @abstractmethod
    def eject(self):
        pass


class CodeInjection(AbstractCodeInjection):
    def __init__(
        self,
        address: ConvertibleToAddress,
        code_to_inject: Code,
    ):
        self.address = ensure_address(address)
        self.code_to_inject = compile_asm(code_to_inject)
        self.original_code: bytes = b""
        self._injected = False

    @override
    def inject(self):
        self.original_code = pm.read_bytes(self.address.resolve(), len(self.code_to_inject))
        pm.write_bytes(self.address.resolve(), self.code_to_inject, len(self.code_to_inject))
        self._injected = True

    @override
    def eject(self):
        if self._injected:
            pm.write_bytes(self.address.resolve(), self.original_code, len(self.original_code))
            self._injected = False


class AllocatingCodeInjection(AbstractCodeInjection):  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        address: ConvertibleToAddress,
        code_to_inject: Code,
        original_code_length: int = 0,
        new_memory_size: int = 1024,
        is_long_x64_jump_needed: Never = Never,
    ):
        if is_long_x64_jump_needed is not Never:
            raise Exception(  # pylint: disable=broad-exception-raised
                "Since TrainerBase 3.4.0 is_long_x64_jump_needed has been deprecated."
                " Now there is not need to manually pop and push rax. That's why you must"
                " rewrite injections based on manual pop rax, push rax and then remove is_long_x64_jump_needed"
                " argument"
            )

        self.address = ensure_address(address)

        self.code_to_inject = compile_asm(code_to_inject)

        if pm.is_64_bit:
            self.code_to_inject = compile_asm("pop rax") + self.code_to_inject + compile_asm("push rax")

        self.original_code: bytes = b""

        self.original_code_length = original_code_length
        self.new_memory_size = new_memory_size
        self.new_memory_address: int = 0

    @override
    def inject(self):
        self.original_code = pm.read_bytes(self.address.resolve(), self.original_code_length)
        self.new_memory_address: int = pm.allocate(self.new_memory_size)

        if pm.is_64_bit:
            new_mem_jump_code_generator = get_long_x64_jump_to_new_mem_code
            jump_back_code_generator = get_long_x64_jump_back_code
        else:
            new_mem_jump_code_generator = get_simple_jump_code
            jump_back_code_generator = get_simple_jump_code

        jump_to_new_mem = compile_asm(new_mem_jump_code_generator(self.new_memory_address))
        jumper_length = len(jump_to_new_mem)

        if jumper_length < self.original_code_length:
            jump_to_new_mem += b"\x90" * (self.original_code_length - len(jump_to_new_mem))
        elif jumper_length > self.original_code_length:
            raise ValueError(f"Jumper length > original code length: {jumper_length} > {self.original_code_length}")

        jump_back_address = self.address.resolve() + jumper_length
        if pm.is_64_bit:
            jump_back_address -= 1

        jump_back = compile_asm(jump_back_code_generator(jump_back_address))
        code_to_inject = self.code_to_inject + jump_back

        pm.write_bytes(self.new_memory_address, code_to_inject, len(code_to_inject))
        pm.write_bytes(self.address.resolve(), jump_to_new_mem, len(jump_to_new_mem))

    @override
    def eject(self):
        if self.new_memory_address:
            pm.write_bytes(self.address.resolve(), self.original_code, self.original_code_length)
            pm.free(self.new_memory_address)
            self.new_memory_address = 0


class MultipleCodeInjection(AbstractCodeInjection):
    def __init__(self, *injections: AbstractCodeInjection):
        self._injections = injections

    @override
    def inject(self):
        for injection in self._injections:
            injection.inject()

    @override
    def eject(self):
        for injection in self._injections:
            injection.eject()


def compile_asm(code: Code) -> bytes:
    if isinstance(code, str):
        fasm_mode = f"use{ARCH}"
        with TemporaryDirectory() as tmp_dir:
            asm_file = Path(tmp_dir) / "injection.asm"

            asm_file.write_text(f"{fasm_mode}\n{code}", encoding="utf-8")

            run_executable([FASM_EXECUTABLE_PATH, asm_file], stdout=DEVNULL, check=True)
            code = asm_file.with_suffix(".bin").read_bytes()

    if not isinstance(code, bytes):
        raise TypeError("code must be bytes | str")

    return code


def get_simple_jump_code(address: int) -> str:
    return f"""
        push {address}
        ret
    """


def get_long_x64_jump_to_new_mem_code(address: int) -> str:
    return f"""
        push rax
        mov rax, {address}
        push rax
        ret
        pop rax
    """


def get_long_x64_jump_back_code(address: int) -> str:
    return f"""
        mov rax, {address}
        push rax
        ret
    """


def safely_eject_all_code_injections() -> None:
    try:
        for injection in AbstractCodeInjection.created_code_injections:
            injection.eject()
    except MemoryWriteError:  # Game process exited
        return
