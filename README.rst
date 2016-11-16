Chronophore
===========
|pypi_version| |license|

.. |pypi_version| image:: https://img.shields.io/pypi/v/chronophore.svg?maxAge=86400
    :target: https://pypi.python.org/pypi/chronophore
.. |license| image:: https://img.shields.io/pypi/l/chronophore.svg
    :target: ./LICENSE

Chronophore is a time-tracking program. It keeps track of users'
hours as they sign in and out.

This project was started to help keep track of students and tutors
signing in and out at a tutoring center in a community college.

Chronophore uses a Qt interface by default, but includes a Tk interface for compatibility:

.. figure:: https://cloud.githubusercontent.com/assets/5744114/20331074/f3a2097a-ab57-11e6-8eb3-e61a268c35f6.png
    :alt: Qt Interface

    Qt Interface

.. figure:: https://cloud.githubusercontent.com/assets/5744114/20331232/f542c520-ab58-11e6-9ff5-c797ab20d850.png
    :alt: Tk Interface

    Tk Interface

Installation
------------

Chronophore can be installed with pip:

.. code-block:: bash

    $ pip install chronophore


Usage
-----

.. code-block::

    usage: chronophore [-h] [--testdb] [-v] [--debug] [-V] [--tk]

    Desktop app for tracking sign-ins and sign-outs in a tutoring center.

    optional arguments:
      -h, --help     show this help message and exit
      --testdb       create and use a database with test users
      -v, --verbose  print a detailed log
      --debug        print debug log
      -V, --version  print version info and exit
      --tk           use old tk interface
