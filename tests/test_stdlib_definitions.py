from collections import Counter, OrderedDict
from enum import Enum
from types import MappingProxyType
from uuid import UUID

from prettyprinter import pformat


def test_counter():
    value = Counter({'a': 1, 'b': 200})
    expected = "collections.Counter({'a': 1, 'b': 200})"
    assert pformat(value, width=999) == expected


def test_ordereddict():
    value = OrderedDict([('a', 1), ('b', 2)])
    expected = "collections.OrderedDict([('a', 1), ('b', 2)])"
    assert pformat(value, width=999) == expected


def test_enum():
    class TestEnum(Enum):
        ONE = 1
        TWO = 2

    value = TestEnum.ONE
    expected = 'tests.test_stdlib_definitions.test_enum.<locals>.TestEnum.ONE'
    assert pformat(value) == expected


def test_mappingproxytype():
    value = MappingProxyType({'a': 1, 'b': 2})
    expected = "mappingproxy({'a': 1, 'b': 2})"
    assert pformat(value) == expected


def test_uuid():
    value = UUID('3ec21c4e-8125-478c-aa2c-c66de452c2eb')
    expected = "uuid.UUID('3ec21c4e-8125-478c-aa2c-c66de452c2eb')"
    assert pformat(value) == expected
