Django Compressor Mako
======================

This module provide `Django Compressor <c>`_ support for `mako template <m>`_.

Usage
=====

All you need to do is to import extension namespace and using it with mako
syntax:

.. code-block:: mako

    <%namespace name="compress" module="django_compressor_mako"/>

    <%compress:compress kind="css">
    <link rel="stylesheet" href="/static/css/style.css" type="text/css" />
    </%compress:compress>

All django-compressor arguments are supported but must be explicitly named:

* ``kind``: mandatory, "css" or "js".
* ``mode``: optional, compressor mode, "file" or "inline".
* ``name``: is not supported and will raise a ``NotImplementedError``

Outputs cannot be named and are just named using hash plus extension.

Also note that mako template doesn't allow blocks inside of ``<%call>``, that
means **you cannot use the following syntax**:

.. code-block:: mako

    <%namespace name="compress" module="django_compressor_mako"/>

    <%compress:compress kind="css">
    <%block name="more_css"/>
    </%compress:compress>

Shorter functions
=================

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

.. _c: https://github.com/django-compressor/django-compressor
.. _m: http://www.makotemplates.org/
