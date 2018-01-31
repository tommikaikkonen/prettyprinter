import ast
import pytest

from prettyprinter import (
    install_extras,
    pformat,
    pprint,
)

install_extras(['ast'])


def test_parsed():
    node = ast.parse('value = 42')
    print(pformat(node, width=999))
    assert pformat(node, width=999) == """\
ast.Module(
    body=[
        ast.Assign(
            targets=[
                ast.Name(id='value', ctx=ast.Store(), lineno=1, col_offset=0)
            ],
            value=ast.Num(n=42, lineno=1, col_offset=8),
            lineno=1,
            col_offset=0
        )
    ]
)"""


@pytest.mark.parametrize('cls, identifier', [
    (ast.Name, 'ast.Name'),
    (type('Name', (ast.Name,), {'__module__': 'custom'}), 'custom.Name'),
])
def test_pure_node(cls, identifier):
    name = cls(id='value')
    assert pformat(name) == "%s(id='value')" % identifier
