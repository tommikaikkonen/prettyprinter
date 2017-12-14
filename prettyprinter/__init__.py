# -*- coding: utf-8 -*-

"""Top-level package for prettyprinter."""

__author__ = """Tommi Kaikkonen"""
__email__ = 'kaikkonentommi@gmail.com'
__version__ = '0.3.1'

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
    - ``'ipython'`` - makes prettyprinter the default printer in the IPython shell.

    :param include: an iterable of strs representing the extras to include.
        All extras are included by default.
    :param exclude: an iterable of strs representing the extras to exclude.
    """
    include = set(include)
    exclude = set(exclude)

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
