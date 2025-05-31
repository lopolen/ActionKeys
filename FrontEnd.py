import sys
from PyQt6.QtWidgets import (
    QApplication,
    QSystemTrayIcon,
    QMenu,
)
from PyQt6.QtGui import QIcon


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, on_stop):
        super().__init__(QIcon('src/icon.png'))
        self.setToolTip("ActionKeys")

        menu = QMenu(None)
        exit_ = menu.addAction("Exit")
        exit_.triggered.connect(lambda: on_stop())

        self.setContextMenu(menu)
        self.show()
        # self.activated.connect(self.func)  # Left click


def run(on_stop):
    app = QApplication(sys.argv)
    tray = SystemTrayIcon(on_stop)
    app.exec()
