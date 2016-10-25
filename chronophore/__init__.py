"""Chronophore is a simple time-tracking program. It keeps track of
users' hours as they sign in and out. Data is stored in a
human-readable json file.

This project was started to help keep track of students signing in
and out at a tutoring program in a community college, but should be
adaptable to other use cases.
"""
from sqlalchemy.orm import sessionmaker

__title__ = 'chronophore'
__version__ = '0.5.0'
__license__ = 'MIT'
__author__ = 'Amin Mesbah'
__email__ = 'mesbahamin@gmail.com'
__description__ = 'Desktop app for tracking sign-ins and sign-outs in a tutoring center.'

Session = sessionmaker()
