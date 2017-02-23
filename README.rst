What is Chronophore?
--------------------

|pypi_version| |docs| |license|

.. |pypi_version| image:: https://img.shields.io/pypi/v/chronophore.svg?maxAge=86400
    :target: https://pypi.python.org/pypi/chronophore
.. |license| image:: https://img.shields.io/pypi/l/chronophore.svg
    :target: ./LICENSE
.. |docs| image:: https://readthedocs.org/projects/chronophore/badge/?version=latest
    :target: https://chronophore.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Chronophore is a time-tracking program. It keeps track of users' hours as they
sign in and out.

This project was started to help keep track of students and tutors signing in
and out at a tutoring center in a community college.

.. figure:: https://cloud.githubusercontent.com/assets/5744114/20331074/f3a2097a-ab57-11e6-8eb3-e61a268c35f6.png
    :alt: Qt Interface


Installation
------------

Chronophore can be installed with pip:

.. code-block:: bash

    $ pip install chronophore


Usage
-----

.. code-block:: text

    usage: chronophore [-h] [--testdb] [-v] [--debug] [-V] [--tk]

    Desktop app for tracking sign-ins and sign-outs in a tutoring center.

    optional arguments:
      -h, --help     show this help message and exit
      --testdb       create and use a database with test users
      -v, --verbose  print a detailed log
      --debug        print debug log
      -V, --version  print version info and exit
      --tk           use old tk interface


Documentation
-------------

Chronophore's Documentation is available at https://chronophore.readthedocs.io.

Hosting is graciously provided by the good people at `Read The Docs`_. Many
thanks!

.. _Read The Docs: https://readthedocs.org
