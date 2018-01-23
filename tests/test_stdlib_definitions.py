from collections import (
    ChainMap,
    Counter,
    OrderedDict,
    defaultdict,
    deque,
    namedtuple,
)
from enum import Enum
from types import MappingProxyType
from uuid import UUID

from prettyprinter import pformat, is_registered


def test_counter():
    value = Counter({'a': 1, 'b': 200})
    expected = "collections.Counter({'a': 1, 'b': 200})"
    assert pformat(value, width=999, sort_dict_keys=True) == expected


def test_ordereddict():
    value = OrderedDict([('a', 1), ('b', 2)])
    expected = "collections.OrderedDict([('a', 1), ('b', 2)])"
    assert pformat(value, width=999, sort_dict_keys=True) == expected


def test_defaultdict():
    value = defaultdict(list)
    assert pformat(value, width=999) == 'collections.defaultdict(list, {})'


def test_deque():
    value = deque([1, 2], maxlen=10)
    assert pformat(value, width=999) == 'collections.deque([1, 2], maxlen=10)'

    value2 = deque([1, 2])
    assert pformat(value2, width=999) == 'collections.deque([1, 2])'


def test_chainmap():
    empty = ChainMap()
    assert pformat(empty, width=999) == 'collections.ChainMap()'

    value = ChainMap({'a': 1}, {'b': 2}, {'a': 1})
    assert pformat(value, width=999) == "collections.ChainMap({'a': 1}, {'b': 2}, {'a': 1})"


def test_enum():
    class TestEnum(Enum):
        ONE = 1
        TWO = 2

    value = TestEnum.ONE
    expected = 'tests.test_stdlib_definitions.test_enum.<locals>.TestEnum.ONE'
    assert pformat(value) == expected


def test_mappingproxytype():
    assert is_registered(
        MappingProxyType,
        check_deferred=True,
        register_deferred=False
    )
    value = MappingProxyType({'a': 1, 'b': 2})
    expected = "mappingproxy({'a': 1, 'b': 2})"
    assert pformat(value, sort_dict_keys=True) == expected


def test_uuid():
    value = UUID('3ec21c4e-8125-478c-aa2c-c66de452c2eb')
    expected = "uuid.UUID('3ec21c4e-8125-478c-aa2c-c66de452c2eb')"
    assert pformat(value) == expected


def test_namedtuple():
    MyClass = namedtuple('MyClass', ['one', 'two'])
    value = MyClass(one=1, two=2)
    constructor_str = 'tests.test_stdlib_definitions.MyClass'
    assert pformat(value, width=999) == constructor_str + '(one=1, two=2)'
