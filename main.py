import socket
import sys
import threading

import FrontEnd
import config
from logger import logger

from button_scripts.both_up import both_up
from button_scripts.btn1_up import btn1_up
from button_scripts.btn2_up import btn2_up


def hardware_listen():
    global running

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(config.HAPI_ADDR)

    logger.info("Connected to Hardware server")
    while running:
        data = client.recv(1024)
        if data:
            command = data.decode(config.ENCODE).strip()
            logger.debug(f'Received Hardware server command: {command}')
            if command == "btn1_up":
                threading.Thread(target=btn1_up).start()
            elif command == "btn2_up":
                threading.Thread(target=btn2_up).start()
            elif command == "both_up":
                threading.Thread(target=both_up).start()

    client.close()


def send_to_root(command: str):
    with socket.create_connection(config.RAIP_ADDR) as sock:
        sock.sendall(command.encode(config.ENCODE))


def stop():
    global running

    logger.info("Stop function start")
    send_to_root('exit')
    running = False
    sys.exit()


if __name__ == '__main__':
    running = True

    threading.Thread(target=hardware_listen).start()
    FrontEnd.run(lambda: stop())
