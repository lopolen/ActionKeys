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
        if exit_callback:
            exit_callback()
        else:
            sys.exit()


class AIItWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("src/aiit_main_window.ui", self)


    def closeEvent(self, event):
        event.ignore()
        self.hide()


    def aiit(self):
        self.show()
        QApplication.processEvents()

        text = pyperclip.paste()
        if not text:
            print("Буфер обміну пустий або текст не виділено")
            return

        self.thread = QThread()
        self.worker = OllamaWorker(text)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.new_text.connect(self.append_text)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()


    def append_text(self, text_chunk: str):
        self.textBrowser.setText(self.textBrowser.toPlainText() + text_chunk)


class OllamaWorker(QObject):
    new_text = pyqtSignal(str)
    finished = pyqtSignal()


    def __init__(self, text):
        super().__init__()
        self.text = text


    def run(self):
        stream = ollama.chat(model='gemma3:4b', messages=[
            {'role': 'user', 'content': self.text}
        ], stream=True)

        for chunk in stream:
            self.new_text.emit(chunk['message']['content'])

        self.finished.emit()
