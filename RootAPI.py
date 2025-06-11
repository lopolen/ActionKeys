import socket
import sys
import threading

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

        conn.close()


def api_exit():
    global ha, rs

    logger.info("Root API exiting")

    ha.stop_api()
    rs.running = False

    sys.exit()


if __name__ == "__main__":
    ha = HardwareAPI(HardwareAPI.find_ch340_port())
    threading.Thread(target=ha.listen).start()

    rs = RootServer()
    rs.server_listen()
