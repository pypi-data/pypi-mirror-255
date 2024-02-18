.. image:: https://github.com/IMIO/imio.pyutils/actions/workflows/main.yml/badge.svg?branch=master
    :target: https://github.com/IMIO/imio.pyutils/actions/workflows/main.yml

.. image:: https://coveralls.io/repos/github/IMIO/imio.pyutils/badge.svg
    :target: https://coveralls.io/github/IMIO/imio.pyutils

.. image:: http://img.shields.io/pypi/v/imio.pyutils.svg
   :alt: PyPI badge
   :target: https://pypi.org/project/imio.pyutils

.. contents::

Introduction
============

This package provides python useful methods.

It relates to following kinds of operations:

1) System level operations (system.py)

It provides helper methods to:

* read and write files,
* read directories,
* execute commands,
* store and load list and dict,
* trace printing,
* creating temporary files,
* etc.

2) Various python helpers (utils.py)

About:

* ordereddict and dict manipulations
* list manipulations
* duration recording

3) BeautifulSoup methods (bs.py)

* remove elements
* remove attributes
* remove comments
* replace entire strings
* unwrap tags

4) Postgres level operations (postgres.py). It requires psycopg2 egg !

It provides helper methods to:

* single or multiple select,
* insert, update, delete rows,
* etc.

Tests
=====

Can be run with: `bin/python -m unittest discover`
