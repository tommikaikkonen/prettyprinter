=======
History
=======

0.9.0 (2018-01-03)
------------------

No breaking changes.

* Added pretty printer definition for ``types.MappingProxyType`` thanks to GitHub user `Cologler <https://github.com/Cologler/>`_
* Added support for ``_repr_pretty_`` in the extra ``ipython_repr_pretty``.


0.8.1 (2018-01-01)
------------------

* Fixed issue #7 where having a ``str`` value for IPython's ``highlighting_style`` setting was not properly handled in ``prettyprinter``'s IPython integration, and raised an exception when trying to print data.

0.8.0 (2017-12-31)
------------------

Breaking changes:

* by default, ``dict`` keys are printed in the default order (insertion order in CPython 3.6+). Previously they were sorted like in the ``pprint`` standard library module. To let the user control this, an additional keyword argument ``sort_dict_keys`` was added to ``cpprint``, ``pprint``, and ``pformat``. Pretty printer definitions can control ``dict`` key sorting with the ``PrettyContext`` instance passed to each pretty printer function.

Non-breaking changes:

* Improved performance of rendering colorized output by caching colors.
* Added ``prettyprinter.pretty_repr`` that is assignable to ``__repr__`` dunder methods, so you don't need to write it separately from the pretty printer definition.
* Deprecated use of ``PrettyContext.set`` in favor of less misleading ``PrettyContext.assoc``
* Defined pretty printing for instances of ``type``, i.e. classes.
* Defined pretty printing for functions



0.7.0 (2017-12-23)
------------------

Breaking change: instances of lists, sets, frozensets, tuples and dicts will be truncated to 1000 elements by default when printing.

* Added pretty printing definitions for ``dataclasses``
* Improved performance of splitting strings to multiple lines by ~15%
* Added a maximum sequence length that applies to subclasses of lists, sets, frozensets, tuples and dicts. The default is 1000. There is a trailing comment that indicates the number of truncated elements. To remove truncation, you can set ``max_seq_len`` to ``None`` using ``set_default_config`` explained below.
* Added ability to change the default global configuration using ``set_default_config``. The functions accepts zero to many keyword arguments and replaces those values in the global configuration with the ones provided.

.. code:: python

    from prettyprinter import set_default_config

    set_default_config(
        style='dark',
        max_seq_len=1000,
        width=79,
        ribbon_width=71,
        depth=None,
    )

0.6.0 (2017-12-21)
------------------

No backwards incompatible changes.

* Added pretty printer definitions for the ``requests`` library. To use it, include ``'requests'`` in your ``install_extras`` call: ``prettyprinter.install_extras(include=['requests'])``.

0.5.0 (2017-12-21)
------------------

No backwards incompatible changes.

* Added integration for the default Python shell
* Wrote docs to explain integration with the default Python shell
* Check ``install_extras`` arguments for unknown extras

0.4.0 (2017-12-14)
------------------

* Revised ``comment`` to accept both normal Python values and Docs, and reversed the argument order to be more Pythonic

0.3.0 (2017-12-12)
------------------

* Add ``set_default_style`` function, improve docs on working with a light background

0.2.0 (2017-12-12)
------------------

* Numerous API changes and improvements.


0.1.0 (2017-12-07)
------------------

* First release on PyPI.
