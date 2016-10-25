import io
import os
import re
from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))


def read(*names, **kwargs):
    with io.open(
        os.path.join(here, *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()


setup(
    name='chronophore',
    version=find_version("chronophore", "__init__.py"),

    description=(
        'Desktop app for tracking sign-ins and sign-outs in a tutoring center.'
    ),

    long_description=long_description,

    url='https://github.com/mesbahamin/chronophore',

    # Author details
    author='Amin Mesbah',
    author_email='mesbahamin@gmail.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        # 3 - Alpha
        # 4 - Beta
        # 5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Office/Business :: Scheduling',

        'License :: OSI Approved :: MIT License',

        'Natural Language :: English',

        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: POSIX :: Linux',

        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
    ],

    keywords='database desktop education sqlite kiosk sign-in time',

    packages=['chronophore'],
    entry_points={
        'gui_scripts': [
            'chronophore=chronophore.chronophore:main',
        ],
    },

    # TODO(amin): remove scripts and openpyxl
    scripts=[
        'scripts/excel_to_json.py',
        'scripts/json_to_excel.py',
        'scripts/json_to_sqlite.py'
    ],
    install_requires=['appdirs>=1.4.0', 'openpyxl>=2.3.5', 'SQLAlchemy>=1.1.2'],

    extras_require={
        'dev': ['flake8'],
        'test': ['pytest'],
    },
)
