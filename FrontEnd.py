import sys

import ollama
import pyperclip
from PyQt6.QtWidgets import (
    QSystemTrayIcon,
    QMenu,
    QMainWindow, QApplication
)
from PyQt6.QtGui import QIcon
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal, QObject, QThread

from logger import guilog

exit_callback = None


class UIController(QObject):
    show_window_signal = pyqtSignal()
    ollama_run_signal = pyqtSignal()

controller = UIController()


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self):
        super().__init__(QIcon('src/icon.png'))
        self.setToolTip("ActionKeys")

        menu = QMenu(None)
        exit_ = menu.addAction("Exit")
        exit_.triggered.connect(self.exit_clicked)

        self.setContextMenu(menu)
        self.show()
        # self.activated.connect(self.func)  # Left click


    def exit_clicked(self):
        guilog.info("Exit button from context menu triggered. Initializing exit function")
        if exit_callback:
            exit_callback()
        else:
            sys.exit()


class AIItWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/aiit_main_window.ui", self)

        self.history = []

        self.sendButton.clicked.connect(self.on_send_click)
        self.clearButton.clicked.connect(self.clear_history)


    def clear_history(self):
        self.history.clear()
        self.textBrowser.setText('')

        guilog.debug("Ollama chat history cleared")


    def closeEvent(self, event):
        event.ignore()
        self.hide()


    def aiit(self, text):
        guilog.debug("Ollama requests started")
        self.history.append({'role': 'user', 'content': text})

        self.textBrowser.append(f"User: {text}")
        self.textBrowser.append(f"Assistant: ")

        self.thread = QThread()
        self.worker = OllamaWorker(text)
        self.worker.moveToThread(self.thread)

        self.thread = QThread()
        self.worker = OllamaWorker(self.history)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.new_text.connect(self.append_text)
        self.worker.finished.connect(self.on_ollama_finished)

        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.thread.quit)

        self.thread.start()


    def append_text(self, text_chunk: str):
        self.textBrowser.setText(self.textBrowser.toPlainText() + text_chunk)


    def on_ollama_finished(self, full_message: str):
        guilog.debug("Ollama request finished")
        self.history.append({"role": "assistant", "content": full_message})


    def on_send_click(self):
        text = self.lineEdit.text()
        self.aiit(text)


    def on_button_signal(self):
        text = pyperclip.paste()
        if not text:
            guilog.warning('No text in clipboard. Aborting function')
            return

        self.show()
        QApplication.processEvents()

        self.aiit(text)


class OllamaWorker(QObject):
    new_text = pyqtSignal(str)
    finished = pyqtSignal(str)


    def __init__(self, history: list):
        super().__init__()
        self.history = history


    def run(self):
        full_response = ""
        stream = ollama.chat(model='gemma3:4b', messages=self.history, stream=True)

        for chunk in stream:
            part = chunk['message']['content']
            full_response += part
            self.new_text.emit(part)

        self.finished.emit(full_response)
