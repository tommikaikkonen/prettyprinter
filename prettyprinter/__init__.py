# -*- coding: utf-8 -*-

"""Top-level package for prettyprinter."""

__author__ = """Tommi Kaikkonen"""
__email__ = 'kaikkonentommi@gmail.com'
__version__ = '0.1.2'

from io import StringIO
import sys

from pprint import isrecursive, isreadable, saferepr
from .color import colored_render_to_stream
from .prettyprinter import (
    python_to_sdocs,
    register_pretty,
    prettycall,
    comment,
    trailing_comment,
)
from .render import default_render_to_stream

# Registers standard library types
# as a side effect
import prettyprinter.pretty_stdlib


__all__ = [
    'PrettyPrinter',
    'pformat',
    'pprint',
    'saferepr',
    'isreadable',
    'isrecursive',
    'default_render_to_stream',
    'python_to_sdocs',
    'cpprint',
    'register_pretty',
    'prettycall',
    'comment',
    'trailing_comment',
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
