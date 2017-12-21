# -*- coding: utf-8 -*-

"""Top-level package for prettyprinter."""

__author__ = """Tommi Kaikkonen"""
__email__ = 'kaikkonentommi@gmail.com'
__version__ = '0.5.0'

from io import StringIO
from importlib import import_module
import sys
import warnings

from pprint import isrecursive, isreadable, saferepr
from .color import colored_render_to_stream, set_default_style
from .prettyprinter import (
    python_to_sdocs,
    register_pretty,
    pretty_call,
    comment,
    trailing_comment,
)
from .render import default_render_to_stream

# Registers standard library types
# as a side effect
import prettyprinter.pretty_stdlib


__all__ = [
    'cpprint',
    'pprint',
    'pformat',
    'install_extras',
    'set_default_style',
    'register_pretty',
    'pretty_call',
    'trailing_comment',
    'comment',
    'python_to_sdocs',
    'default_render_to_stream',
    'PrettyPrinter',
    'saferepr',
    'isreadable',
    'isrecursive',
]


class PrettyPrinter:
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def pprint(self, object):
        pprint(*self._args, **self._kwargs)

    def pformat(self, object):
        return pformat(*self._args, **self._kwargs)

    def isrecursive(self, object):
        return isrecursive(object)

    def isreadable(self, object):
        return isreadable(object)

    def format(self, object):
        raise NotImplementedError


def pformat(
    object,
    indent=4,
    width=79,
    depth=None,
    *,
    ribbon_width=71,
    compact=False
):
    # TODO: compact
    sdocs = python_to_sdocs(
        object,
        indent=indent,
        width=width,
        depth=depth,
        ribbon_width=ribbon_width,
    )
    stream = StringIO()
    default_render_to_stream(stream, sdocs)
    return stream.getvalue()


def pprint(
    object,
    stream=None,
    indent=4,
    width=79,
    depth=None,
    *,
    compact=False,
    ribbon_width=71,
    end='\n'
):
    """Pretty print a Python value ``object`` to ``stream``,
    which defaults to sys.stdout. The output will not be colored.

    :param indent: number of spaces to add for each level of nesting.
    :param stream: the output stream, defaults to sys.stdout
    :param width: a soft maximum allowed number of columns in the output,
                  which the layout algorithm attempts to stay under.
    :param depth: maximum depth to print nested structures
    :param ribbon_width: a soft maximum allowed number of columns in the output,
                         after indenting the line
    """
    # TODO: compact
    sdocs = python_to_sdocs(
        object,
        indent=indent,
        width=width,
        depth=depth,
        ribbon_width=ribbon_width,
    )
    if stream is None:
        stream = sys.stdout
    default_render_to_stream(stream, sdocs)
    if end:
        stream.write(end)


def cpprint(
    object,
    stream=None,
    indent=4,
    width=79,
    depth=None,
    *,
    compact=False,
    ribbon_width=71,
    style=None,
    end='\n'
):
    """Pretty print a Python value ``object`` to ``stream``,
    which defaults to sys.stdout. The output will be colored and
    syntax highlighted.

    :param indent: number of spaces to add for each level of nesting.
    :param stream: the output stream, defaults to sys.stdout
    :param width: a soft maximum allowed number of columns in the output,
                  which the layout algorithm attempts to stay under.
    :param depth: maximum depth to print nested structures
    :param ribbon_width: a soft maximum allowed number of columns in the output,
                         after indenting the line
    :param style: one of ``'light'``, ``'dark'`` or a subclass
                  of ``pygments.styles.Style``. If omitted,
                  will use the default style. If the default style
                  is not changed by the user with :func:`~prettyprinter.set_default_style`,
                  the default is ``'dark'``.
    """
    sdocs = python_to_sdocs(
        object,
        indent=indent,
        width=width,
        depth=depth,
        ribbon_width=ribbon_width
    )
    if stream is None:
        stream = sys.stdout
    colored_render_to_stream(stream, sdocs, style=style)
    if end:
        stream.write(end)


ALL_EXTRAS = frozenset([
    'attrs',
    'django',
    'ipython',
    'python',
    'requests',
])
EMPTY_SET = frozenset()


def install_extras(
    include=ALL_EXTRAS,
    *,
    exclude=EMPTY_SET,
    raise_on_error=False,
    warn_on_error=True
):
    """Installs extras. The following extras are available:

    - ``'attrs'`` - automatically pretty prints classes created using the ``attrs`` package.
    - ``'django'`` - automatically pretty prints Model and QuerySet ubclasses defined in your Django apps.
    - ``'requests'`` - automatically pretty prints Requests, Responses, Sessions, etc.
    - ``'ipython'`` - makes prettyprinter the default printer in the IPython shell.
    - ``'python'`` - makes prettyprinter the default printer in the default Python shell.

    :param include: an iterable of strs representing the extras to include.
        All extras are included by default.
    :param exclude: an iterable of strs representing the extras to exclude.
    """
    include = set(include)
    exclude = set(exclude)

    unexisting_extras = (include | exclude) - ALL_EXTRAS

    if unexisting_extras:
        raise ValueError(
            "The following extras don't exist: {}".format(
                ', '.join(unexisting_extras)
            )
        )

    extras_to_install = (ALL_EXTRAS & include) - exclude

    for extra in extras_to_install:
        module_name = 'prettyprinter.extras.' + extra
        try:
            extra_module = import_module(module_name)
        except ImportError as e:
            if raise_on_error:
                raise e
            if warn_on_error:
                warnings.warn(
                    "Failed to import '{0}' PrettyPrinter extra. "
                    "If you don't need it, call install_extras with "
                    "exclude=['{0}']".format(extra)
                )
        else:
            try:
                extra_module.install()
            except Exception as exc:
                if raise_on_error:
                    raise exc
                elif warn_on_error:
                    warnings.warn(
                        "Failed to install '{0}' PrettyPrinter extra. "
                        "If you don't need it, call install_extras with "
                        "exclude=['{0}']".format(extra)
                    )
