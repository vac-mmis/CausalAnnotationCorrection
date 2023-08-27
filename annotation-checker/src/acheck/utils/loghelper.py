import logging
import sys
import threading

console_lock = threading.Lock()


class ConsoleLock:

    __instance = None
    lock = threading.Lock()

    def __new__(cls):
        if cls.__instance is None:
            cls._instance = super().__new__(cls)
        return cls.__instance




def setup_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s [%(threadName)s] %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)
    return logger


logger1 = setup_logger("thread1")
logger2 = setup_logger("thread2")


def worker1():
    with lock:
        logger1.debug("Debug message")
        logger1.info("Info message")
        logger1.warning("Warning message")
        logger1.error("Error message")


def worker2():
    with lock:
        logger2.debug("Debug message")
        logger2.info("Info message")
        logger2.warning("Warning message")
        logger2.error("Error message")
