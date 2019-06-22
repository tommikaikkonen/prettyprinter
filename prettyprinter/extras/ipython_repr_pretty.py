from contextlib import contextmanager

from .ipython import OriginalRepresentationPrinter
from ..utils import (
    compose,
    identity,
)
from ..prettyprinter import (
    register_pretty,
    pretty_python_value,
)
from ..doc import (
    HARDLINE,
    concat,
    contextual,
    flat_choice,
    group,
    nest
)


def implements_repr_pretty(instance):
    try:
        method = instance._repr_pretty_
        # Values returned from Mocks don't have a __func__
        # attribute.
        method.__func__
    except AttributeError:
        return False
    return callable(method)


class NoopStream:
    def write(self, value):
        pass


class CompatRepresentationPrinter(OriginalRepresentationPrinter):
    def __init__(self, *args, **kwargs):
        self._prettyprinter_ctx = kwargs.pop('prettyprinter_ctx')
        super().__init__(*args, **kwargs)

        # self.output should be assigned by the superclass
        assert isinstance(self.output, NoopStream)

        self._pending_wrapper = identity
        self._docparts = []

    def text(self, obj):
        super().text(obj)

        self._docparts.append(obj)

    def breakable(self, sep=' '):
        super().breakable(sep)

        self._docparts.append(
            flat_choice(when_flat=sep, when_broken=HARDLINE)
        )

    def begin_group(self, indent=0, open=''):
        super().begin_group(indent, open)

        def wrapper(doc):
            if indent:
                doc = nest(indent, doc)
            return group(doc)

        self._pending_wrapper = compose(wrapper, self._pending_wrapper)

    def end_group(self, dedent=0, close=''):
        super().end_group(dedent, close)

        # dedent is ignored; it is not supported to
        # have different indentation when starting and
        # ending the group.

        doc = self._pending_wrapper(concat(self._docparts))

        self._docparts = [doc]
        self._pending_wrapper = identity

    @contextmanager
    def indent(self, indent):
        """with statement support for indenting/dedenting."""
        curr_docparts = self._docparts
        self._docparts = []
        self.indentation += indent
        try:
            yield
        finally:
            self.indentation -= indent
            indented_docparts = self._docparts
            self._docparts = curr_docparts
            self._docparts.append(nest(indent, concat(indented_docparts)))

    def pretty(self, obj):
        self._docparts.append(
            pretty_python_value(obj, self._prettyprinter_ctx)
        )


def wrap_repr_pretty(fn):
    def wrapped(value, ctx):
        def evaluator(indent, column, page_width, ribbon_width):
            printer = CompatRepresentationPrinter(
                NoopStream(),
                max_width=page_width - column,
                max_seq_length=ctx.max_seq_len,
                prettyprinter_ctx=ctx
            )

            with printer.group():
                fn(value, printer, cycle=False)

            return concat(printer._docparts)
        return contextual(evaluator)
    return wrapped


def pretty_repr_pretty(value, ctx):
    unbound_repr_pretty = value._repr_pretty_.__func__
    return wrap_repr_pretty(unbound_repr_pretty)(value, ctx)


def install():
    register_pretty(predicate=implements_repr_pretty)(pretty_repr_pretty)
