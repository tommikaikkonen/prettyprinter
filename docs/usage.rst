=====
Usage
=====

Install the package with ``pip``:

.. code:: bash
    
    pip install prettyprinter

Then, instead of

.. code:: python

    from pprint import pprint

do

.. code:: python

    from prettyprinter import cpprint

for colored output. For colorless output, remove the ``c`` prefix from the function name:

.. code:: python

    from prettyprinter import pprint



Usage in Python code
--------------------

Call :func:`~prettyprinter.cpprint` for colored output or :func:`~prettyprinter.pprint` for uncolored output, just like ``pprint.pprint``:

.. code:: python

    >>> from prettyprinter import cpprint
    >>> cpprint({'a': 1, 'b': 2})
    {'a': 1, 'b': 2}

The default style is meant for a dark background. If you're on a light background, or want to set your own theme, you may do so with :func:`~prettyprinter.set_default_style`

.. code:: python
    
    >>> from prettyprinter import set_default_style
    >>> set_default_style('light')

Possible values are ``'light'``, ``'dark'``, and any subclass of ``pygments.styles.Style``.

+++++++++++++++++++++++++++++++++++++++++++++++++++++
Adding a pretty printer function to the global namespace
+++++++++++++++++++++++++++++++++++++++++++++++++++++

If you're so inclined, you could add :func:`~prettyprinter.cpprint` to the global namespace in your application so you can use it in a similar way as the built in ``print`` function:

.. code:: python
    
    import builtins
    import prettyprinter
    builtins.pretty = prettyprinter.cpprint

    pretty([1, 2, 3])

You'll want to add this to a file that is executed during application initialization.


Usage with IPython
------------------

You can use prettyprinter with IPython so that values in the REPL will be printed with ``prettyprinter`` using syntax highlighting. You need to call ``prettyprinter`` initialization functions at the start of an IPython session, which IPython facilitates with `profile startup files`_. To initialize prettyprinter in your default profile, add and edit a new startup file with the following commands:

.. code:: bash
    
    touch "`ipython locate profile default`/startup/init_prettyprinter.py"
    nano "`ipython locate profile default`/startup/init_prettyprinter.py"


The code in this file will be run upon entering the shell. Add these lines and comment out any extra packages you don't need:

.. code:: python

    # Specify syntax higlighting theme in IPython;
    # will be picked up by prettyprinter.
    from pygments import styles

    # For light terminal backgrounds.
    from prettyprinter.color import GitHubLightStyle
    ipy = get_ipython()
    ipy.colors = 'LightBG'
    ipy.highlighting_style = GitHubLightStyle

    # For dark terminal background.
    ipy = get_ipython()
    ipy.colors = 'linux'
    ipy.highlighting_style = styles.get_style_by_name('monokai')

    import prettyprinter

    prettyprinter.install_extras(
        # Comment out any packages you are not using.
        include=[
            'ipython',
            'attrs',
            'django',
            'requests',
            'dataclasses',
        ],
        warn_on_error=True
    )


Usage in the default Python shell
---------------------------------

PrettyPrinter integrates with the default shell by overriding ``sys.displayhook``, so that values evaluated in the prompt will be printed using PrettyPrinter. The integration is set up as follows:

.. code:: python

    >>> from prettyprinter import install_extras
    >>> install_extras(['python'])
    >>> {'a': 1, 'b': 2}
    {'a': 1, 'b': 2}  # <- this will be colored when run in a terminal.

If you don't want to run this every time you open a shell, create a Python startup file that executes the above statements and point the environment variable ``PYTHONSTARTUP`` to that file in your shell initialization file (such as ``~/.bashrc``), and rerun ``~/.bashrc`` to assign the correct ``PYTHONSTARTUP`` value in your current shell session. Here's a bash script to do that for you:

.. code:: bash
    
    echo 'import prettyprinter; prettyprinter.install_extras(["python"])\n' >> ~/python_startup.py
    echo "\nexport PYTHONSTARTUP=~/python_startup.py" >> ~/.bashrc
    source ~/.bashrc

If you're using a light background in your terminal, run this to add a line to the Python startup file to change the color theme PrettyPrinter uses:

.. code:: bash

    echo '\nprettyprinter.set_default_style("light")' >> ~/python_startup.py


Then, after starting the ``python`` shell,

.. code:: bash
    
    python

values evaluated in the shell should be printed with PrettyPrinter without any other setup.

.. code:: python
    
    >>> {'a': 1, 'b': 2}
    {'a': 1, 'b': 2} # <- the output should be colored when run in a terminal.


Pretty printing your own types
------------------------------

Given a custom class:

.. code:: python

    class MyClass(object):
        def __init__(self, one, two):
            self.one = one
            self.two = two


You can register a pretty printer:

.. code:: python

    from prettyprinter import register_pretty, pretty_call

    @register_pretty(MyClass)
    def pretty_myclass(value, ctx):
        return pretty_call(
            ctx,
            MyClass,
            one=value.one,
            two=value.two
        )


To get an output like this with simple data:

.. code:: python
    
    >>> prettyprinter.pprint(MyClass(1, 2))
    MyClass(one=1, two=2)

The real utility is in how nested data pretty printing is handled for you, and how the function call is broken to multiple lines for easier legibility:

.. code:: python
    
    >>> prettyprinter.pprint(MyClass({'abc': 1, 'defg': 2, 'hijk': 3}, [1, 2]))
    MyClass(
        one={
            'abc': 1,
            'defg': 2,
            'hijk': 3
        },
        two=[1, 2]
    )

:func:`@register_pretty <prettyprinter.register_pretty>` is a decorator that takes the type to register. Internally, :class:`functools.singledispatch` is used to handle dispatch to the correct pretty printer. This means that any subclasses will also use the same printer.

The decorated function must accept exactly two positional arguments:

- ``value`` to pretty print, and
- ``ctx``, a context value.

In most cases, you don't need need to do anything with the context, except pass it along in nested calls. It can be used to affect rendering of nested data.

The function must return a :class:`~prettyprinter.doc.Doc`, which is either an instance of :class:`~prettyprinter.doc.Doc` or a :class:`str`. :func:`~prettyprinter.pretty_call` returns a :class:`~prettyprinter.doc.Doc` that represents a function call. Given an arbitrary context ``ctx``

.. code:: python

    pretty_call(ctx, round, 1.5)

Will be printed out as

.. code:: python

    round(1.5)

with syntax highlighting.


.. _`profile startup files`: http://ipython.readthedocs.io/en/stable/config/intro.html#profiles
.. _colorful: https://github.com/timofurrer/colorful
.. _pygments: https://pypi.python.org/pypi/Pygments