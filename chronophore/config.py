import appdirs
import configparser
import logging
import os
import pathlib
from collections import OrderedDict

from chronophore import __title__


logger = logging.getLogger(__name__)


def _load_config(config_file):
    """Load settings from config file and return them as
    a dict.
    """

    parser = configparser.ConfigParser()

    try:
        with config_file.open('r') as f:
            parser.read_file(f)
    except FileNotFoundError as e:
        logger.warning('Config file not found')
        parser = _use_default(config_file)
    except configparser.ParsingError as e:
        logger.warning('Error in config file: {}'.format(e))
        parser = _use_default(config_file)
    finally:
        config = dict(
            VALIDATE_USERS=parser.getboolean('validation', 'validate_users'),
            USER_ID_LENGTH=parser.getint('validation', 'user_id_length'),
            MESSAGE_DURATION=parser.getint('gui', 'message_duration'),
            GUI_WELCOME_LABLE=parser.get('gui', 'gui_welcome_label'),
            LARGE_FONT_SIZE=parser.getint('gui', 'large_font_size'),
            MEDIUM_FONT_SIZE=parser.getint('gui', 'medium_font_size'),
            SMALL_FONT_SIZE=parser.getint('gui', 'small_font_size'),
            TINY_FONT_SIZE=parser.getint('gui', 'tiny_font_size'),
        )
        logger.debug('Config loaded: {}'.format(config_file))

        return config


def _use_default(config_file):
    """Write default values to a config file. Return
    a ConfigParser object with the values loaded.
    """

    default_config = OrderedDict((
        (
            'validation',
            OrderedDict(
                (
                    ('validate_users', True),
                    ('user_id_length', 9),
                )
            ),
        ),
        (
            'gui',
            OrderedDict(
                (
                    ('message_duration', 5),
                    ('gui_welcome_label', 'Welcome to the STEM Learning Center!'),
                    ('large_font_size', 30),
                    ('medium_font_size', 18),
                    ('small_font_size', 15),
                    ('tiny_font_size', 10),
                )
            ),
        ),
    ))

    parser = configparser.ConfigParser()
    parser.read_dict(default_config)

    with config_file.open('w') as f:
        parser.write(f)

    logger.info('Default config file created.')

    return parser


CONFIG_FILE = pathlib.Path(appdirs.user_config_dir(__title__), 'config.ini')
os.makedirs(str(CONFIG_FILE.parent), exist_ok=True)
CONFIG = _load_config(CONFIG_FILE)
