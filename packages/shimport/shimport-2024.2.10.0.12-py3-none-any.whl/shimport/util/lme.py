""" {{pkg}}.util.lme
"""

import sys
import logging

from shimport import constants


def set_global_level(level):
    """https://stackoverflow.com/questions/19617355/dynamically-changing-log-level-without-restarting-the-application

    :param level:

    """
    logger = logging.getLogger()
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
        # if isinstance(handler, type(logging.StreamHandler())):
        #     handler.setLevel(logging.DEBUG)
        #     logger.debug('Debug logging enabled')


def get_logger(name, console=sys.stderr):
    """
    utility function for returning a logger
    with standard formatting patterns, etc
    """
    log_handler = logging.StreamHandler(stream=console)

    logging.basicConfig(
        format="%(message)s",
        datefmt="[%X]",
        handlers=[log_handler],
    )
    FormatterClass = logging.Formatter
    formatter = FormatterClass(
        fmt=" ".join(["%(name)s", "%(message)s"]),
        # datefmt="%Y-%m-%d %H:%M:%S",
        datefmt="",
    )
    log_handler.setFormatter(formatter)

    logger = logging.getLogger(name)

    # FIXME: get this from some kind of global config
    # logger.setLevel("DEBUG")
    logger.setLevel(constants.LOG_LEVEL.upper())

    return logger
