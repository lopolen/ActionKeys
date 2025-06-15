import time
from RootAPI import root
from FrontEnd import controller


def btn2_up():
    root({"command": "imitate_keyboard", "args": "ctrl+c"})
    time.sleep(0.2)

    controller.ollama_run_signal.emit()
