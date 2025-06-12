import webbrowser
import pyperclip
import time
from RootAPI import root


def btn1_up():
    root({"command": "imitate_keyboard", "args": "ctrl+c"})

    time.sleep(0.1)

    text = pyperclip.paste()
    if not text:
        print("Буфер обміну пустий або текст не виділено")
        return
    query = text.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
