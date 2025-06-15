import socket
import sys
import threading

import FrontEnd
import config
from logger import guilog
from RootAPI import root

from button_scripts.both_up import both_up
from button_scripts.btn1_up import btn1_up
from button_scripts.btn2_up import btn2_up

from PyQt6.QtWidgets import QApplication


def hardware_listen():
    global running

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(config.HAPI_ADDR)

    guilog.info("Connected to Hardware server")
    while running:
        data = client.recv(1024)
        if data:
            command = data.decode(config.ENCODE).strip()
            if command == "btn1_up":
                guilog.info("Button 1 up received")
                threading.Thread(target=btn1_up).start()
            elif command == "btn2_up":
                guilog.info("Button 2 up received")
                threading.Thread(target=btn2_up).start()
            elif command == "both_up":
                guilog.info("Both-up received")
                threading.Thread(target=both_up).start()
            else:
                guilog.warning(f'Received wrong command from HardwareAPI: {command}')

    client.close()


def stop():
    global running

    guilog.info("Stopping ActionKeys")
    root({"command": 'exit'})
    running = False
    app.quit()

FrontEnd.exit_callback = stop


if __name__ == '__main__':
    running = True

    app = QApplication(sys.argv)
    tray = FrontEnd.SystemTrayIcon()
    aiit_window = FrontEnd.AIItWindow()

    FrontEnd.controller.show_window_signal.connect(aiit_window.show)
    FrontEnd.controller.ollama_run_signal.connect(aiit_window.on_button_signal)

    threading.Thread(target=hardware_listen).start()
    app.exec()
