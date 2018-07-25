import pytest  # noqa

from prettyprinter import (
    pformat,
)
import prettyprinter.extras.ipython_repr_pretty

prettyprinter.extras.ipython_repr_pretty.install()


def test_compat():
    class MyClass:
        def _repr_pretty_(self, p, cycle):
            with p.group(0, '{', '}'):
                with p.indent(4):
                    p.breakable(sep='')
                    p.text("'a': ")
                    p.pretty(1)
                    p.text(',')
                    p.breakable(sep=' ')
                    p.text("'b': ")
                    p.pretty(2)
                p.breakable(sep='')

    result = pformat(MyClass())
    expected = """{'a': 1, 'b': 2}"""
    assert result == expected

    result = pformat(MyClass(), width=12)
    expected = """\
{
    'a': 1,
    'b': 2
}"""

    assert result == expected
