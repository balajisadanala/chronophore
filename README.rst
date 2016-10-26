Chronophore
===========
|pypi_version| |license|

.. |pypi_version| image:: https://img.shields.io/pypi/v/chronophore.svg?maxAge=86400
    :target: https://pypi.python.org/pypi/chronophore
.. |license| image:: https://img.shields.io/pypi/l/chronophore.svg
    :target: ./LICENSE

Screenshot
----------
.. figure:: docs/screenshot_program.png
    :alt: Tk interface

Chronophore is a time-tracking program. It keeps track of users'
hours as they sign in and out.

This project was started to help keep track of students signing in and
out at a tutoring center in a community college.


Installation
------------

Chronophore can be installed with pip:

.. code-block:: bash
    
    $ pip install chronophore
    

Usage
-----

.. code-block::

    usage: chronophore [-h] [--testdb] [-v] [--debug] [-V]

    Desktop app for tracking sign-ins and sign-outs in a tutoring center.

    optional arguments:
      -h, --help     show this help message and exit
      --testdb       create and use a database with test users
      -v, --verbose  print a detailed log
      --debug        print debug log
      -V, --version  print version info and exit
