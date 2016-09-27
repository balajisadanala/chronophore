import appdirs
import logging
import os
import pathlib
from datetime import datetime

from chronophore import __title__
from chronophore.model import Timesheet
from chronophore.view import ChronophoreUI


def set_up_logging(log_file):
    logger = logging.getLogger()
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
    # Make Chronophor's directories and files in $HOME
    DATA_DIR = pathlib.Path(appdirs.user_data_dir(__title__))
    os.makedirs(str(DATA_DIR), exist_ok=True)

    LOG_FILE = pathlib.Path(appdirs.user_log_dir(__title__), 'debug.log')
    os.makedirs(str(LOG_FILE.parent), exist_ok=True)

    _today = datetime.strftime(datetime.today(), "%Y-%m-%d")
    DATA_FILE = DATA_DIR.joinpath(_today + '.json')
    USERS_FILE = DATA_DIR.joinpath('users.json')

    logger = set_up_logging(LOG_FILE)
    logger.debug("Program initialized")
    logger.debug('Data Directory: {}'.format(DATA_DIR))
    logger.debug('Log File: {}'.format(LOG_FILE))

    t = Timesheet(data_file=DATA_FILE, users_file=USERS_FILE)
    ChronophoreUI(timesheet=t)

    logger.debug("Program stopping")
