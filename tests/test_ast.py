import ast
import pytest

from prettyprinter import (
    install_extras,
    pformat,
    pprint,
)


def test_parsed():
    node = ast.parse('value = 42')
    assert pformat(node, width=999) == """\
ast.Module(
    body=[
        ast.Assign(
            targets=[ast.Name(id='value', ctx=ast.Store())],
            value=ast.Num(n=42)
        )
    ]
)"""


@pytest.mark.parametrize('cls, identifier', [
    (ast.Name, 'ast.Name'),
    (type('Name', (ast.Name,), {'__module__': 'custom'}), 'custom.Name'),
])
def test_pure_node(cls, identifier):
    name = cls(id='value', ctx=None)
    assert pformat(name) == "%s(id='value', ctx=None)" % identifier
