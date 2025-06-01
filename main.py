import sys
import subprocess
import time

import RootAPI, FrontEnd
import threading

from button_scripts.both_up import both_up
from button_scripts.btn1_up import btn1_up
from button_scripts.btn2_up import btn2_up


def start_hardware_api() -> subprocess.Popen:
    return subprocess.Popen(
        ['sudo', '/home/nikita/PycharmProjects/ActionKeys/.venv/bin/python', 'RootAPI.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )


def listen_to_hardware(proc_: subprocess.Popen):
    while True:
        line = proc_.stdout.readline()
        if not line:
            break
        line = line.strip()
        if line == "btn1_up":
            btn1_up(proc_)

        time.sleep(0.01)


def stop():
    global proc

    proc.stdin.write("exit\n")
    proc.stdin.flush()
    proc.terminate()

    sys.exit()


if __name__ == '__main__':
    proc = start_hardware_api()
    threading.Thread(target=lambda: listen_to_hardware(proc)).start()

    FrontEnd.run(lambda: stop())
