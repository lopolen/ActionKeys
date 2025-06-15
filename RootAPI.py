import json
import socket
import subprocess
import sys
import threading
from json import JSONDecodeError

import keyboard

import config
from HardwareAPI import HardwareAPI
from logger import rootlog


class RootServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(config.RAIP_ADDR)
        self.server.settimeout(1.0)

        self.running = True


    def server_listen(self):
        self.server.listen()

        rootlog.info("RootServer listen started")

        while self.running:
            try:
                conn, addr = self.server.accept()
                threading.Thread(target=lambda: self.client_handler(conn)).start()
            except socket.timeout:
                continue
            except OSError as err:
                rootlog.exception(err)
                break


    def client_handler(self, conn):
        rootlog.debug("New connection to RootServer")

        while self.running:
            msg = conn.recv(1024)
            if msg:
                command = msg.decode(config.ENCODE).strip()

                try:
                    command = json.loads(command)
                    if command['command'] == 'exit':
                        rootlog.info("Exit command received")
                        api_exit()

                    if command['command'] == "imitate_keyboard":
                        rootlog.info(f"Imitating {command['args']} press-release")
                        keyboard.press_and_release(command['args'])

                    if command['command'] == "cmd":
                        rootlog.info(f"cmd: {command['args']}")
                        subprocess.Popen(command['args'])

                except JSONDecodeError:
                    rootlog.warning(f"Invalid command sent: {command}")
                    continue

        conn.close()


def api_exit():
    global ha, rs

    rootlog.info("RootAPI stopping")

    ha.stop_api()
    rs.running = False

    sys.exit()


def root(command: dict):
    with socket.create_connection(config.RAIP_ADDR) as sock:
        sock.send(json.dumps(command).encode(config.ENCODE))


if __name__ == "__main__":
    ha = HardwareAPI(HardwareAPI.find_ch340_port())
    threading.Thread(target=ha.listen).start()

    rs = RootServer()
    rs.server_listen()
