Django Compressor Mako
======================

.. image:: https://codecov.io/gh/orus-io/django-compressor-mako/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/orus-io/django-compressor-mako

.. image:: https://travis-ci.org/orus-io/django-compressor-mako.svg?branch=master
    :target: https://travis-ci.org/orus-io/django-compressor-mako

.. image:: https://img.shields.io/pypi/v/django_compressor_mako.svg
    :target: https://pypi.python.org/pypi/django_compressor_mako

This module provide `mako template`_ support for `Django Compressor`_.

Usage
-----

All you need to do is to import extension namespace and using it with mako
syntax:

.. code-block:: mako

    <%namespace name="compress" module="django_compressor_mako"/>

    <%compress:compress kind="css">
    <link rel="stylesheet" href="/static/css/style.css" type="text/css" />
    </%compress:compress>

Almost all django-compressor arguments are supported but must be explicitly
named:

* ``kind``: mandatory, "css" or "js".
* ``mode``: optional, compressor mode, "file" or "inline".
* ``name``: is not supported and will raise a ``NotImplementedError``

Outputs **cannot** be named and are just named using hash plus extension.

Also note that mako template doesn't allow blocks inside of ``<%call>``, that
means **you cannot use the following syntax**:

.. code-block:: mako

    <%namespace name="compress" module="django_compressor_mako"/>

    <%compress:compress kind="css">
    <%block name="more_css"/>
    </%compress:compress>

Offline compression
-------------------

In order to use offline compression you must first create cached compressed
files and manifest using ``python ./manage.py compress_mako``.

Shorter functions
-----------------

Additionally two shorter functions are provided, ``css`` and ``js``, same
arguments can be passed except ``kind`` which is set by default depending on
which one is used, eg.:

.. code-block:: mako

    <%namespace name="compress" module="django_compressor_mako"/>

    <%compress:css>
    <link rel="stylesheet" href="/static/css/style.css" type="text/css" />
    </%compress:css>

    <%compress:js>
    <script type="text/javascript" src="/static/js/script.js">
    </%compress:js>

.. _Django Compressor: https://github.com/django-compressor/django-compressor
.. _mako template: http://www.makotemplates.org/
