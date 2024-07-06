import logging

from .color_formatter import ColoredFormatter


def setup_loggers_color():
    logging.basicConfig(level=logging.DEBUG, format="[%(name)s] %(message)s", handlers=[logging.StreamHandler()])
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        colored_formatter = ColoredFormatter(handler.formatter._fmt)
        handler.setFormatter(colored_formatter)


def get_console_logger(name):
    return logging.getLogger(name)
