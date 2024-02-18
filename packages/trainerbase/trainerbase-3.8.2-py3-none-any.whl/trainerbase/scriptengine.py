from collections.abc import Callable
from sys import stderr
from threading import Thread
from time import sleep

from pymem.exception import MemoryReadError, MemoryWriteError


class Script:
    def __init__(self, callback: Callable, enabled: bool = False):
        self.callback = callback
        self.enabled = enabled

    def __repr__(self):
        return f"<Script {getattr(self.callback, '__name__', 'Anon')}:" f" enabled={self.enabled}" f">"

    def __call__(self):
        return self.callback()


class ScriptEngine:
    def __init__(self, delay: float = 0.05):
        self.delay = delay
        self.should_run = False
        self.thread = Thread(target=self.script_loop)
        self.scripts: list[Script] = []

    def __repr__(self):
        return f"<ScriptEngine delay={self.delay} should_run={self.should_run} scripts={len(self.scripts)}>"

    def start(self):
        self.should_run = True
        self.thread.start()

    def stop(self):
        self.should_run = False
        self.thread.join()

    def script_loop(self):
        while self.should_run:
            for script in self.scripts:
                if not script.enabled:
                    continue

                try:
                    script()
                except (MemoryReadError, MemoryWriteError):
                    continue
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(e, file=stderr)
                    self.stop()

            sleep(self.delay)

    def register_script(self, script: Script) -> Script:
        self.scripts.append(script)
        return script

    def simple_script(self, executor: Callable) -> Script:
        script = Script(executor)
        self.register_script(script)
        return script


def enabled_by_default(script: Script) -> Script:
    script.enabled = True
    return script


system_script_engine = ScriptEngine()
