import socket
import threading
import time

import serial
from serial.tools import list_ports

import config
from logger import rootlog


class HardwareAPI:
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

        self.ignore_next_single_up = None
        self.waiting_for_release = None
        self.both_pressed = None
        self.btn1_down_time = 0
        self.btn2_down_time = 0
        self.btn1_up_time = 0
        self.btn2_up_time = 0

        self.on_btn1_up = lambda: self.server.send_all("btn1_up")
        self.on_btn2_up = lambda: self.server.send_all("btn2_up")
        self.on_both_up = lambda: self.server.send_all("both_up")

    PRESS_SYNC_TIMEOUT = 0.1
    RELEASE_SYNC_TIMEOUT = 0.1

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
                now = time.time()

                # Saving time data
                if btn1 and not self.btn1_last:
                    self.btn1_down_time = now
                if btn2 and not self.btn2_last:
                    self.btn2_down_time = now
                if not btn1 and self.btn1_last:
                    self.btn1_up_time = now
                if not btn2 and self.btn2_last:
                    self.btn2_up_time = now

                # --- Both down logic ---
                both_pressed_now = btn1 and btn2
                both_pressed_sync = abs(self.btn1_down_time - self.btn2_down_time) <= self.PRESS_SYNC_TIMEOUT

                if both_pressed_now and both_pressed_sync and not self.both_pressed:
                    self.both_pressed = True
                    self.waiting_for_release = True
                    self.ignore_next_single_up = True
                    rootlog.debug("Both pressed")

                # --- Up logic ---
                if self.both_pressed and self.waiting_for_release:
                    if not btn1 and not btn2:
                        release_diff = abs(self.btn1_up_time - self.btn2_up_time)
                        if release_diff <= self.RELEASE_SYNC_TIMEOUT:
                            rootlog.debug("Both up")
                            threading.Thread(target=self.on_both_up).start()
                        else:
                            rootlog.debug(f"Desynced release ({release_diff:.3f}s). Ignore.")
                        self.reset_state()
                        self.btn1_last = btn1
                        self.btn2_last = btn2
                        continue

                # --- Single buttons ---
                if not self.both_pressed:
                    if not btn1 and self.btn1_last and not self.ignore_next_single_up:
                        rootlog.debug("Button 1 up")
                        threading.Thread(target=self.on_btn1_up).start()

                    if not btn2 and self.btn2_last and not self.ignore_next_single_up:
                        rootlog.debug("Button 2 up")
                        threading.Thread(target=self.on_btn2_up).start()

                self.btn1_last = btn1
                self.btn2_last = btn2

            time.sleep(0.005)

    def reset_state(self):
        self.both_pressed = False
        self.waiting_for_release = False
        self.ignore_next_single_up = False


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
