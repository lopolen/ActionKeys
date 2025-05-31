import threading

import serial
import time
import logging


class HardwareAPI:
    BOTH_RELEASE_TIMEOUT = 0.05  # 50 мс

    def __init__(self, com_port: str):
        self.ser = serial.Serial(com_port, 9600)
        self.running = True

        self.btn1_last = False
        self.btn2_last = False

        self.both_pressed = False
        self.waiting_for_second_up = False
        self.first_up_time = 0
        self.first_up_button = None

        self.on_btn1_up = lambda: logging.info("No function set to btn1_up")
        self.on_btn2_up = lambda: logging.info("No function set to btn2_up")
        self.on_both_up = lambda: logging.info("No function set to both_up")


    def data_reset(self):
        self.both_pressed = False
        self.waiting_for_second_up = False
        self.first_up_button = None


    def listen(self):
        while self.running:
            if self.ser.in_waiting > 0:
                try:
                    data = int(self.ser.readline().decode().strip())
                except ValueError:
                    continue  # Некоректні дані

                btn1 = bool((data >> 0) & 1)
                btn2 = bool((data >> 1) & 1)

                # --- Обробка кнопок ---
                # Обидві натиснуті
                if btn1 and btn2 and not self.btn1_last and not self.btn2_last:
                    self.both_pressed = True

                # Перше відпускання
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

                # Друге відпускання
                if self.both_pressed and self.waiting_for_second_up:
                    second_released = (
                        (not btn1 and self.btn1_last and self.first_up_button != "btn1") or
                        (not btn2 and self.btn2_last and self.first_up_button != "btn2")
                    )

                    if second_released:
                        threading.Thread(target=self.on_both_up).start()
                        self.data_reset()
                    elif time.time() - self.first_up_time > self.BOTH_RELEASE_TIMEOUT:
                        # Занадто довго чекали — виконуємо одинарне up
                        if self.first_up_button == "btn1":
                            threading.Thread(target=self.on_btn1_up).start()
                        else:
                            threading.Thread(target=self.on_btn2_up).start()
                        self.data_reset()

                # Окремі up, якщо не чекали обидві
                if not self.both_pressed and not btn1 and self.btn1_last:
                    self.on_btn1_up()

                if not self.both_pressed and not btn2 and self.btn2_last:
                    self.on_btn2_up()

                # Оновлення станів
                self.btn1_last = btn1
                self.btn2_last = btn2

            time.sleep(0.01)
