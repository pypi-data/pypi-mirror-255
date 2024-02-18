import logging
import os
from logging.handlers import QueueHandler, QueueListener, TimedRotatingFileHandler
from queue import Queue

from .settings import get_settings

odm_logger = logging.getLogger("odm")


def init_logger():
    """
    Initialisiert den ODM-Logger
    :return: None
    """

    settings = get_settings()

    logger = logging.getLogger()
    logger.setLevel(logging.getLevelNamesMapping()[settings.logLevel.upper()])

    logger.handlers.clear()

    queue = Queue(-1)
    queue_handler = QueueHandler(queue)
    logger.addHandler(queue_handler)

    formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]   %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if not os.path.exists("logs") or not os.path.isdir("logs"):
        os.makedirs("logs")

    file_handler = TimedRotatingFileHandler("logs/odm.log", when="midnight", interval=1, backupCount=7)
    file_handler.setFormatter(formatter)

    queue_listener = QueueListener(queue, console_handler, file_handler, respect_handler_level=True)
    queue_listener.start()

    __reset_sub_loggers()


def __reset_sub_loggers():
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.handlers.clear()
        logger.filters.clear()


def log_info(text):
    """
    Loggt eine Info-Nachricht
    :param text: Text
    :return: None
    """

    odm_logger.info(text)


def log_warning(text):
    """
    Loggt eine Warnung
    :param text: Text
    :return: None
    """

    odm_logger.warning(text)


def log_error(text):
    """
    Loggt einen Fehler
    :param text: Text
    :return: None
    """

    odm_logger.error(text)


def log_exception(text):
    """
    Loggt eine Exception
    :param text: Text
    :return: None
    """

    odm_logger.exception(text)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        odm_logger.log(record.levelno, record.getMessage())
