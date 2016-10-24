import appdirs
import argparse
import logging
import os
import pathlib
from sqlalchemy import create_engine

from chronophore import (
    __description__, __title__, __version__, controller, Session
)
from chronophore.models import Base, add_test_users
from chronophore.view import ChronophoreUI


def get_args():
    parser = argparse.ArgumentParser(
        prog=__title__,
        description=__description__,
    )
    parser.add_argument(
        '--testdb', action='store_true',
        help='create and use a database with test users'
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='print a detailed log'
    )
    parser.add_argument(
        '--debug', action='store_true',
        help='print debug log'
    )
    parser.add_argument(
        '-V', '--version', action='store_true',
        help='print version info and exit'
    )
    return parser.parse_args()


def set_up_logging(log_file, console_log_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(str(log_file))
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(console_log_level)
    formatter = logging.Formatter(
        "{asctime} {levelname} ({name}): {message}", style='{'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def main():
    args = get_args()

    # Make Chronophore's directories and files in $HOME
    DATA_DIR = pathlib.Path(appdirs.user_data_dir(__title__))
    LOG_FILE = pathlib.Path(appdirs.user_log_dir(__title__), 'debug.log')
    os.makedirs(str(DATA_DIR), exist_ok=True)
    os.makedirs(str(LOG_FILE.parent), exist_ok=True)

    if args.version:
        print('{} {}'.format(__title__, __version__))
        raise SystemExit

    if args.debug:
        CONSOLE_LOG_LEVEL = logging.DEBUG
    elif args.verbose:
        CONSOLE_LOG_LEVEL = logging.INFO
    else:
        CONSOLE_LOG_LEVEL = logging.WARNING

    logger = set_up_logging(LOG_FILE, CONSOLE_LOG_LEVEL)
    logger.debug('-'*80)
    logger.debug('{} {}'.format(__title__, __version__))
    logger.debug('Log File: {}'.format(LOG_FILE))
    logger.debug('Data Directory: {}'.format(DATA_DIR))

    if args.testdb:
        DATABASE_FILE = DATA_DIR.joinpath('test.sqlite')
        logger.info('Using test database.')
    else:
        DATABASE_FILE = DATA_DIR.joinpath('chronophore.sqlite')

    logger.debug('Database File: {}'.format(DATABASE_FILE))
    engine = create_engine('sqlite:///{}'.format(str(DATABASE_FILE)))
    Base.metadata.create_all(engine)
    Session.configure(bind=engine)

    if args.testdb:
        add_test_users(session=Session())

    controller.auto_sign_out(session=Session())

    ChronophoreUI()

    logger.debug('{} stopping'.format(__title__))
