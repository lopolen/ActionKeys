import sys

import HardwareAPI, FrontEnd
import threading

from button_scripts.both_up import both_up
from button_scripts.btn1_up import btn1_up
from button_scripts.btn2_up import btn2_up


def stop():
    global ha
    ha.running = False
    sys.exit()


if __name__ == '__main__':
    ha = HardwareAPI.HardwareAPI("COM3")
    ha.on_btn1_up = lambda: btn1_up()
    ha.on_btn2_up = lambda: btn2_up()
    ha.on_both_up = lambda: both_up()

    threading.Thread(target=ha.listen).start()
    on_stop = lambda: stop()
    FrontEnd.run(on_stop)
