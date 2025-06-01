import webbrowser
import pyperclip
import time


def btn1_up(proc_):
    proc_.stdin.write("ctrlc\n")
    proc_.stdin.flush()
    time.sleep(0.1)

    # Отримуємо текст з буфера обміну
    text = pyperclip.paste()
    if not text:
        print("Буфер обміну пустий або текст не виділено")
        return
    # Формуємо URL пошуку Google
    query = text.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}"
    # Відкриваємо браузер
    webbrowser.open(url)
