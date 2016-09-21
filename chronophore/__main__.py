import appdirs
import logging
import os
import pathlib

from . import __title__
from chronophore.view import ChronophoreUI
from chronophore.model import Timesheet


def set_up_logger(log_file):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(str(log_file))
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    formatter = logging.Formatter(
        "{asctime} {levelname} ({name}): {message}", style='{'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def main():
    name = __title__.lower()

    CONFIG_DIR = pathlib.Path(appdirs.user_config_dir(name))
    DATA_DIR = pathlib.Path(appdirs.user_data_dir(name))
    LOG_DIR = pathlib.Path(appdirs.user_log_dir(name))

    os.makedirs(str(CONFIG_DIR), exist_ok=True)
    os.makedirs(str(DATA_DIR), exist_ok=True)
    os.makedirs(str(LOG_DIR), exist_ok=True)

    # CONFIG_FILE = CONFIG_DIR.joinpath(name + '.conf')
    LOG_FILE = LOG_DIR.joinpath('debug.log')

    logger = set_up_logger(LOG_FILE)

    logger.debug("Program initialized")
    logger.debug('Configuration Directory: {}'.format(CONFIG_DIR))
    logger.debug('Data Directory: {}'.format(DATA_DIR))
    logger.debug('Log Directory: {}'.format(LOG_DIR))

    ChronophoreUI(timesheet=Timesheet())

    logger.debug("Program stopping")


if __name__ == '__main__':
    main()
