=============
PrettyPrinter
=============

Syntax-highlighting, declarative and composable pretty printer for Python 3.6+

- Drop in replacement for the standard library ``pprint``: just rename ``pprint`` to ``prettyprinter`` in your imports.
- Uses a modified Wadler-Leijen layout algorithm for optimal formatting
- Write pretty printers for your own types with a dead simple, declarative interface

.. image:: prettyprinterscreenshot.png
    :alt: 

.. image:: ../prettyprinterscreenshot.png
    :alt: 

Packaged with the following pretty printer definitions:

- ``datetime`` - (installed by default)
- ``enum`` - (installed by default)
- ``pytz`` - (installed by default)
- ``attrs`` - any new class you create will be pretty printed automatically
- ``django`` - your Models and QuerySets will be pretty printed automatically

* Free software: MIT license
* Documentation: https://prettyprinter.readthedocs.io.
