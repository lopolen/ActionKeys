import json
import socket
import subprocess
import sys
import threading
from json import JSONDecodeError

import keyboard

import config
from HardwareAPI import HardwareAPI
from logger import logger


class RootServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(config.RAIP_ADDR)
        self.server.settimeout(1.0)

        self.running = True


    def server_listen(self):
        self.server.listen()

        logger.info("RootServer listen started")

        while self.running:
            try:
                conn, addr = self.server.accept()
                threading.Thread(target=lambda: self.client_handler(conn)).start()
            except socket.timeout:
                continue
            except OSError as err:
                logger.exception(err)
                break


    def client_handler(self, conn):
        logger.debug("New conn on RootServer")

        while self.running:
            msg = conn.recv(1024)
            if msg:
                command = msg.decode(config.ENCODE).strip()
                if command == 'exit':
                    logger.debug("Exit command sent")
                    api_exit()

                try:
                    command = json.loads(command)
                    if command['command'] == "imitate_keyboard":
                        logger.info(f"Imitating {command['args']} press and release")
                        keyboard.press_and_release(command['args'])

                    if command['command'] == "cmd":
                        logger.info(f"cmd: {command['args']}")
                        subprocess.Popen(command['args'])

                except JSONDecodeError:
                    logger.warning(f"Invalid command sent: {command}")
                    continue

        conn.close()


def api_exit():
    global ha, rs

    logger.info("Root API exiting")

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
