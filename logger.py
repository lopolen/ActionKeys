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

logger = logging.getLogger("ActionKeys")
logger.setLevel(logging.DEBUG)

file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3
)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | %(threadName)s | %(message)s'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
