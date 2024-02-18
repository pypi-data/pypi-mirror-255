import logging
from colorlog import ColoredFormatter

level = logging.DEBUG


def setup_logger(name):
    """Set up a logger with a ColoredFormatter.
   :param name:
   :return: """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    ch.setFormatter(formatter)

    logger.addHandler(ch)
    return logger
