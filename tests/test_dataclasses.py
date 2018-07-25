from dataclasses import (
    dataclass,
    field,
)
from typing import Any

from prettyprinter import install_extras, pformat

install_extras(['dataclasses'])


@dataclass
class MyClass:
    one: Any
    optional: Any = field(default=1)
    optional2: Any = field(default_factory=list)


def test_simple_case():
    value = MyClass(1)
    expected = "tests.test_dataclasses.MyClass(one=1)"
    assert pformat(value, width=999) == expected


def test_different_from_default():
    value = MyClass(1, optional=2, optional2=[1])
    expected = "tests.test_dataclasses.MyClass(one=1, optional=2, optional2=[1])"
    assert pformat(value, width=999) == expected


@dataclass
class MyOtherClass:
    one: Any = field(repr=False)


def test_no_repr_field():
    value = MyOtherClass(1)
    expected = "tests.test_dataclasses.MyOtherClass()"
    assert pformat(value, width=999) == expected
