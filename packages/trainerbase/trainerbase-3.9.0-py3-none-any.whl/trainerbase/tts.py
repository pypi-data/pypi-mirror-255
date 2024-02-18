from threading import Thread

from pyttsx3 import init as init_tts_engine


engine = init_tts_engine()


def say(text: str, rate: int = 210, volume: float = 1.0, sync=False):
    args = (text, rate, volume)

    if sync:
        say_sync(*args)
    else:
        Thread(target=say_sync, args=args).start()


def say_sync(text: str, rate: int, volume: float):
    engine.stop()

    try:
        engine.endLoop()
    except RuntimeError:
        pass

    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    engine.say(text)

    try:
        engine.runAndWait()
    except RuntimeError:
        pass
