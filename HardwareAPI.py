import socket
import threading
import time

import serial
from serial.tools import list_ports

import config
from logger import rootlog


class HardwareAPI:
    BOTH_RELEASE_TIMEOUT = 0.05  # 50 мс


    class APIServer:
        def __init__(self):
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(config.HAPI_ADDR)
            self.server.settimeout(1.0)
            self.conns = []

            self.running = True

        def server_listen(self):
            self.server.listen()

            rootlog.info("Hardware server listen start")
            while self.running:
                try:
                    conn, addr = self.server.accept()
                    self.conns.append(conn)
                except socket.timeout:
                    continue
                except OSError:
                    break

            self.server.close()

        def send_all(self, msg: str):
            dead_conns = []
            for conn in self.conns:
                try:
                    conn.send(msg.encode(config.ENCODE))
                except (BrokenPipeError, ConnectionResetError, OSError):
                    dead_conns.append(conn)

            self.delete_dead_conns(dead_conns)

        def delete_dead_conns(self, dead_conns: list[socket.socket]):
            for conn in dead_conns:
                self.conns.remove(conn)
                try:
                    conn.close()
                except OSError:
                    pass


    def __init__(self, com_port: str):
        self.server = self.APIServer()

        self.ser = serial.Serial(com_port, 9600)
        rootlog.info(f"HardwareAPI connected to {com_port} device")

        self.running = True

        self.btn1_last = False
        self.btn2_last = False

        self.both_pressed = False
        self.waiting_for_second_up = False
        self.first_up_time = 0
        self.first_up_button = None

        self.on_btn1_up = lambda: self.server.send_all("btn1_up")
        self.on_btn2_up = lambda: self.server.send_all("btn2_up")
        self.on_both_up = lambda: self.server.send_all("both_up")


    def data_reset(self):
        self.both_pressed = False
        self.waiting_for_second_up = False
        self.first_up_button = None


    def listen(self):
        threading.Thread(target=self.server.server_listen).start()

        while self.running:
            if self.ser.in_waiting > 0:
                try:
                    data = int(self.ser.readline().decode().strip())
                except ValueError:
                    rootlog.warning('Wrong data sent from device!')
                    continue

                btn1 = bool((data >> 0) & 1)
                btn2 = bool((data >> 1) & 1)

                # --- Keys handling ---
                # Both pressed
                if btn1 and btn2 and not self.btn1_last and not self.btn2_last:
                    self.both_pressed = True

                # First key-up
                if self.both_pressed and not self.waiting_for_second_up:
                    if not btn1 and self.btn1_last:
                        self.first_up_button = "btn1"
                        self.first_up_time = time.time()
                        self.waiting_for_second_up = True
                        self.btn1_last = btn1
                        self.btn2_last = btn2
                        continue
                    elif not btn2 and self.btn2_last:
                        self.first_up_button = "btn2"
                        self.first_up_time = time.time()
                        self.waiting_for_second_up = True
                        self.btn1_last = btn1
                        self.btn2_last = btn2
                        continue

                # Second key-up
                if self.both_pressed and self.waiting_for_second_up:
                    second_released = (
                        (not btn1 and self.btn1_last and self.first_up_button != "btn1") or
                        (not btn2 and self.btn2_last and self.first_up_button != "btn2")
                    )

                    if second_released:
                        rootlog.debug("Both up event")
                        threading.Thread(target=self.on_both_up).start()
                        self.data_reset()
                    elif time.time() - self.first_up_time > self.BOTH_RELEASE_TIMEOUT:
                        # Both keys up timeout
                        if self.first_up_button == "btn1":
                            rootlog.debug("Timeout. Both up event did not register, button 1 up event registered instead")
                            threading.Thread(target=self.on_btn1_up).start()
                        else:
                            rootlog.debug("Timeout. Both up event did not register, button 2 up event registered instead")
                            threading.Thread(target=self.on_btn2_up).start()
                        self.data_reset()

                # Single button-up
                if not self.both_pressed and not btn1 and self.btn1_last:
                    rootlog.debug("Button 1 up event")
                    threading.Thread(target=self.on_btn1_up).start()

                if not self.both_pressed and not btn2 and self.btn2_last:
                    rootlog.debug("Button 2 up event")
                    threading.Thread(target=self.on_btn2_up).start()

                # Оновлення станів
                self.btn1_last = btn1
                self.btn2_last = btn2

            time.sleep(0.01)


    def stop_api(self):
        rootlog.info("HardwareAPI stopping")
        self.running = False
        self.server.running = False


    @staticmethod
    def find_ch340_port():
        ports = list_ports.comports()
        for port in ports:
            if "1A86:7523" in port.hwid.upper():  # CH340 USB ID
                return port.device  # e.g., "COM3" on Windows or "/dev/ttyUSB0" on Linux
        return None
