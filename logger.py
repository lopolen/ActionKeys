import logging
import logging.handlers
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE = os.path.join(LOG_DIR, "ActionKeys.log")

os.makedirs(LOG_DIR, exist_ok=True)

# Перевіряємо чи файл існує, якщо ні — створюємо з правами 666
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "a"):
        os.utime(LOG_FILE, None)
    os.chmod(LOG_FILE, 0o666)

rootlog = logging.getLogger("RootLog")
rootlog.setLevel(logging.DEBUG)

guilog = logging.getLogger("GUILog")
guilog.setLevel(logging.DEBUG)

file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3
)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(threadName)s | %(message)s'
)
file_handler.setFormatter(formatter)
rootlog.addHandler(file_handler)
guilog.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
rootlog.addHandler(console_handler)
guilog.addHandler(console_handler)
