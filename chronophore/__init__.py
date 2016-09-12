"""Chronophore is a simple time-tracking program. It keeps track of
users' hours as they sign in and out. Data is stored in a
human-readable json file.

This project was started to help keep track of students signing in
and out at a tutoring program in a community college, but should be
adaptable to other use cases.
"""

import logging

# Information
__license__ = 'MIT'
__version__ = '0.2.0'
__author__ = 'Amin Mesbah'
__email__ = 'mesbahamin@gmail.com'

# Set up logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('debug.log')
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
logging.basicConfig(level=logging.DEBUG)
