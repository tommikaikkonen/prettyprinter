#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `prettyprinter` package."""

import pytest
import datetime
import pytz
import sys
from io import StringIO
from itertools import cycle, islice
import json
import timeit

from hypothesis import given, settings, HealthCheck
from hypothesis.extra.pytz import timezones
from hypothesis import strategies as st
from prettyprinter import (
    pprint,
    pformat,
    cpprint,
    pretty_repr,
    register_pretty,
    is_registered,
    pretty_call_alt,
)
from pprint import (
    pprint as nativepprint,
    pformat as nativepformat,
)
from prettyprinter.doc import (
    align,
    concat,
    HARDLINE,
    LINE,
    fill,
)
from prettyprinter.utils import intersperse
from prettyprinter.prettyprinter import str_to_lines
from prettyprinter import (
    comment,
    trailing_comment,
)
from prettyprinter.render import default_render_to_str
from prettyprinter.layout import layout_smart


def test_align():
    doc = concat([
        'lorem ',
        align(
            concat([
                'ipsum',
                HARDLINE,
                'aligned!'
            ])
        )
    ])

    expected = """\
lorem ipsum
      aligned!"""

    res = default_render_to_str(layout_smart(doc))
    assert res == expected


def test_fillsep():
    doc = fill(intersperse(
            LINE,
            islice(
                cycle(["lorem", "ipsum", "dolor", "sit", "amet"]),
                20
            )
        )
    )

    expected = """\
lorem ipsum dolor sit
amet lorem ipsum dolor
sit amet lorem ipsum
dolor sit amet lorem
ipsum dolor sit amet"""
    res = default_render_to_str(layout_smart(doc, width=20))
    assert res == expected


def test_always_breaking():
    """A dictionary value that is broken into multiple lines must
    also break the whole dictionary to multiple lines."""
    data = {
        'okay': ''.join(islice(cycle(['ab' * 20, ' ' * 3]), 3)),
    }
    expected = """\
{
    'okay':
        'abababababababababababababababababababab   '
        'abababababababababababababababababababab'
}"""
    res = pformat(data)
    assert res == expected


def test_pretty_json():
    with open('tests/sample_json.json') as f:
        data = json.load(f)

    print('native pprint')
    nativepprint(data)
    print('prettyprinter')
    cpprint(data)


@pytest.mark.skip(reason="unskip to run performance test")
def test_perf():
    with open('tests/sample_json.json') as f:
        data = json.load(f)

    print('native pprint')
    native_dur = timeit.timeit(
        'nativepformat(data)',
        globals={
            'nativepformat': nativepformat,
            'data': data,
        },
        number=500,
    )
    # nativepprint(data, depth=2)
    print('prettyprinter')
    prettyprinter_dur = timeit.timeit(
        'pformat(data)',
        globals={
            'pformat': pformat,
            'data': data,
        },
        number=500,
    )

    print('Native pprint took {}, prettyprinter took {}'.format(
        native_dur,
        prettyprinter_dur,
    ))


def test_recursive():
    d = {}
    d['self_recursion'] = d

    rendered = pformat(d)
    expected = "{{'self_recursion': <Recursion on dict with id={}>}}".format(
        id(d)
    )
    assert rendered == expected


def possibly_commented(strategy):
    @st.composite
    def _strategy(draw):
        value = draw(strategy)

        add_trailing_comment = False
        if isinstance(value, (list, tuple, set)):
            add_trailing_comment = draw(st.booleans())

        add_comment = draw(st.booleans())

        if add_trailing_comment:
            comment_text = draw(st.text(alphabet='abcdefghijklmnopqrstuvwxyz #\\\'"'))
            value = trailing_comment(value, comment_text)

        if add_comment:
            comment_text = draw(st.text(alphabet='abcdefghijklmnopqrstuvwxyz #\\\'"'))
            value = comment(value, comment_text)

        return value

    return _strategy()


def primitives():
    return (
        st.integers() |
        st.floats(allow_nan=False) |
        st.text() |
        st.binary() |
        st.datetimes(timezones=timezones() | st.none()) |
        st.dates() |
        st.times(timezones=timezones() | st.none()) |
        st.timedeltas() |
        st.booleans() |
        st.none()
    )


hashable_primitives = (
    st.booleans() |
    st.integers() |
    st.floats(allow_nan=False) |
    st.text() |
    st.binary() |
    st.datetimes() |
    st.timedeltas()
)


def identity(x):
    return x


def hashables():
    def extend(base):
        return base.flatmap(
            lambda strat: st.tuples(
                strat,
                st.sampled_from([
                    st.tuples,
                    st.frozensets,
                ])
            )
        ).map(lambda strat__extend: strat__extend[1](strat__extend[0]))

    return st.recursive(hashable_primitives, extend)


def hashable_containers(primitives):
    def extend(base):
        return st.one_of(
            st.frozensets(base),
            st.lists(base).map(tuple),
        )
    return st.recursive(primitives, extend)


def containers(primitives):
    def extend(base):
        return st.one_of(
            st.lists(base),
            st.lists(base).map(tuple),
            st.dictionaries(keys=hashable_containers(primitives), values=base),
        )

    return st.recursive(primitives, extend)


@settings(
    # This is a heavy test, but it's especially
    # slow on Python 3.5.
    suppress_health_check=[HealthCheck.too_slow]
)
@given(
    possibly_commented(
        containers(
            possibly_commented(
                primitives() | primitives().map(type)
            )
        )
    )
)
def test_all_python_values(value):
    cpprint(value)


@settings(max_examples=500, max_iterations=500)
@given(st.binary())
def test_bytes_pprint_equals_repr(bytestr):
    reprd = repr(bytestr)
    pformatted = pformat(bytestr)

    # This is not always the case. E.g.:
    # >>> print(repr(b"\"''"))
    # >>> b'"\'\''
    #
    # Where as prettyprinter chooses
    # >>> print(pformat(b"\"''""))
    # >>> b"\"''"
    # For fewer escapes.
    used_same_quote_type = reprd[-1] == pformatted[-1]

    if used_same_quote_type:
        assert pformat(bytestr) == repr(bytestr)


@settings(max_examples=500, max_iterations=500)
@given(containers(primitives()))
def test_readable(value):
    formatted = pformat(value)

    _locals = {'datetime': datetime, 'pytz': pytz}
    evald = eval(formatted, None, _locals)
    assert evald == value


def nested_dictionaries():
    simple_strings_alphabet = 'abcdefghijklmnopqrstuvwxyz\'"\r\n '
    simple_text = st.text(alphabet=simple_strings_alphabet, min_size=5, average_size=20)

    def extend(base):
        return st.one_of(
            st.lists(base, min_size=5),
            st.dictionaries(keys=simple_text, values=base, min_size=1)
        )

    return st.recursive(simple_text, extend, max_leaves=50)


def test_top_level_str():
    """Tests that top level strings are not indented or surrounded with parentheses"""

    pprint('ab' * 50)
    expected = (
        "'ababababababababababababababababababababababababababababababababababa'"
        "\n'bababababababababababababababab'"
    )
    assert pformat('ab' * 50) == expected


def test_second_level_str():
    """Test that second level strs are indented"""
    expected = """\
[
    'ababababababababababababababababababababababababababababababababababa'
        'bababababababababababababababab',
    'ababababababababababababababababababababababababababababababababababa'
        'bababababababababababababababab'
]"""
    res = pformat(['ab' * 50] * 2)
    assert res == expected


def test_single_element_sequence_multiline_strategy():
    """Test that sequences with a single str-like element are not hang-indented
    in multiline mode."""
    expected = """\
[
    'ababababababababababababababababababababababababababababababababababa'
    'bababababababababababababababab'
]"""
    res = pformat(['ab' * 50])
    assert res == expected


def test_str_bug():
    data = 'lorem ipsum dolor sit amet ' * 10
    expected = """\
'lorem ipsum dolor sit amet lorem ipsum dolor sit amet lorem ipsum '
'dolor sit amet lorem ipsum dolor sit amet lorem ipsum dolor sit amet '
'lorem ipsum dolor sit amet lorem ipsum dolor sit amet lorem ipsum '
'dolor sit amet lorem ipsum dolor sit amet lorem ipsum dolor sit amet '"""
    res = pformat(data)
    assert res == expected



def test_many_cases():
    # top-level multiline str.
    pprint('abcd' * 40)

    # sequence with multiline strs.
    pprint(['abcd' * 40] * 5)

    # nested dict
    pprint({
        'ab' * 40: 'cd' * 50
    })

    # long urls.
    pprint([
        'https://www.example.com/User/john/files/Projects/prettyprinter/images/original/image0001.jpg'
            '?q=verylongquerystring&maxsize=1500&signature=af429fkven2aA'
            '#content1-header-something-something'
    ] * 5)
    nativepprint([
        'https://www.example.com/User/john/files/Projects/prettyprinter/images/original/image0001.jpg'
            '?q=verylongquerystring&maxsize=1500&signature=af429fkven2aA'
            '#content1-header-something-something'
    ] * 5)


def test_datetime():
    pprint(datetime.datetime.utcnow().replace(tzinfo=pytz.utc), width=40)
    pprint(datetime.timedelta(weeks=2, days=1, hours=3, milliseconds=5))
    neg_td = -datetime.timedelta(weeks=2, days=1, hours=3, milliseconds=5)
    pprint(neg_td)


@given(nested_dictionaries())
def test_nested_structures(value):
    pprint(value)


def test_large_data_performance():
    data = [
        {
            'text': 'lorem ipsum dolor sit amet ' * 500
        }
    ] * 200
    stream = StringIO()

    start = datetime.datetime.now()
    cpprint(data, stream=stream)
    stream.getvalue()

    end = datetime.datetime.now()
    took = end - start
    print('took', took)
    # The bottleneck is in string to doc conversion,
    # specifically escaping strings many times.
    # There's probably more we can do here
    assert took < datetime.timedelta(seconds=13)


@settings(max_examples=5000, max_iterations=5000)
@given(
    st.text(),
    st.integers(min_value=5),
    st.sampled_from(('"', "'"))
)
def test_str_to_lines(s, max_len, use_quote):
    lines = list(str_to_lines(max_len, use_quote, s))

    for line in lines:
        assert line
        assert len(line) <= max_len * len('\\Uxxxxxxxx')

    assert ''.join(lines) == s


def test_is_registered():
    class MyClass:
        pass

    assert not is_registered(MyClass)

    # object is not counted as a subclass
    assert not is_registered(MyClass, check_superclasses=True)

    @register_pretty(MyClass)
    def pretty_myclass(instance, ctx):
        return '...'

    assert is_registered(MyClass)
    assert is_registered(MyClass, check_superclasses=True)


def test_is_registered_subclass():
    class MyList(list):
        pass

    assert not is_registered(MyList)
    assert is_registered(MyList, check_superclasses=True)


def test_pretty_repr():
    class MyClass:
        __repr__ = pretty_repr

    @register_pretty(MyClass)
    def pretty_myclass(value, ctx):
        return pretty_call_alt(ctx, MyClass)

    assert repr(MyClass()) == pformat(MyClass())


def test_pretty_repr_unregistered_uses_default_repr_and_warns():
    class MyClass:
        __repr__ = pretty_repr

    inst = MyClass()

    with pytest.warns(UserWarning) as record:
        result = repr(inst)

    assert result == object.__repr__(inst)
    assert len(record) == 1


def test_dict_sorted_by_insertion():
    """dict keys should be printed
    in insertion order."""
    if sys.version_info >= (3, 6):
        value = {
            'x': 1,
            'a': 2
        }
        expected = """{'x': 1, 'a': 2}"""
        assert pformat(value, sort_dict_keys=False) == expected


def test_sort_dict_keys():
    value = {
        'x': 1,
        'a': 2
    }
    expected = """{'a': 2, 'x': 1}"""
    assert pformat(value, sort_dict_keys=True) == expected


def test_dict_subclass():
    class MyDict(dict):
        pass

    empty = MyDict()
    constructor_str = 'tests.test_prettyprinter.test_dict_subclass.<locals>.MyDict'
    assert pformat(empty) == constructor_str + '()'

    value = MyDict({'a': 1})
    assert pformat(value) == constructor_str + "({'a': 1})"

    truncated = MyDict({'a': 1, 'b': 2})
    assert pformat(truncated, max_seq_len=1) == constructor_str + """\
({
    'a': 1
    # ...and 1 more elements
})"""


def test_list_subclass():
    class MyList(list):
        pass

    empty = MyList()
    constructor_str = 'tests.test_prettyprinter.test_list_subclass.<locals>.MyList'
    assert pformat(empty) == constructor_str + '()'

    value = MyList([1, 2])
    assert pformat(value) == constructor_str + "([1, 2])"

    truncated = MyList([1, 2])
    assert pformat(truncated, max_seq_len=1) == constructor_str + """\
([
    1,
    # ...and 1 more elements
])"""


class TestDeferredType(dict):
    pass


def test_deferred_registration():
    expected = 'Deferred type works.'

    assert not is_registered(TestDeferredType, register_deferred=False)

    @register_pretty('tests.test_prettyprinter.TestDeferredType')
    def pretty_testdeferredtype(value, ctx):
        return expected

    assert not is_registered(
        TestDeferredType,
        check_deferred=False,
        register_deferred=False
    )
    assert is_registered(
        TestDeferredType,
        register_deferred=False
    )

    assert pformat(TestDeferredType()) == expected

    # Printer should have been moved to non-deferred registry
    assert is_registered(
        TestDeferredType,
        check_deferred=False,
        register_deferred=False
    )


class BaseTestDeferredType(dict):
    pass


class ConcreteTestDeferredType(BaseTestDeferredType):
    pass


def test_deferred_registration_subclass():
    """Registering a printer for BaseTestDeferredType should be resolved
    when using the subclass ConcreteTestDeferredType"""

    expected = 'Deferred type works.'

    @register_pretty('tests.test_prettyprinter.BaseTestDeferredType')
    def pretty_testdeferredtype(value, ctx):
        return expected

    assert not is_registered(
        ConcreteTestDeferredType,
        check_superclasses=False,
        register_deferred=False
    )

    assert is_registered(
        ConcreteTestDeferredType,
        check_superclasses=True,
        register_deferred=False
    )

    assert pformat(ConcreteTestDeferredType()) == expected
    assert is_registered(
        ConcreteTestDeferredType,
        check_superclasses=True,
        check_deferred=False,
        register_deferred=False
    )
    assert pformat(ConcreteTestDeferredType()) == expected


def test_bad_printer_caught():
    class MyClass:
        pass

    @register_pretty(MyClass)
    def pretty_myclass(value, ctx):
        raise ValueError(value)

    value = MyClass()

    with pytest.warns(UserWarning, match='Falling back to default repr') as record:
        result = pformat(value)

    assert result == repr(value)
    assert len(record) == 1
