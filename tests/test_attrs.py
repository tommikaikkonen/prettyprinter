from attr import attrs, attrib, Factory

from prettyprinter import install_extras, pformat

install_extras(['attrs'])


@attrs
class MyClass:
    one = attrib()
    optional = attrib(default=1)
    optional2 = attrib(default=Factory(list))


def test_simple_case():
    value = MyClass(1)
    expected = "tests.test_attrs.MyClass(one=1)"
    assert pformat(value, width=999) == expected


def test_different_from_default():
    value = MyClass(1, optional=2, optional2=[1])
    expected = "tests.test_attrs.MyClass(one=1, optional=2, optional2=[1])"
    assert pformat(value, width=999) == expected


@attrs
class MyOtherClass:
    one = attrib(repr=False)


def test_no_repr_field():
    value = MyOtherClass(1)
    expected = "tests.test_attrs.MyOtherClass()"
    assert pformat(value, width=999) == expected
