from collections import OrderedDict

from attr import Factory, NOTHING
from prettyprinter.prettyprinter import pretty_call, register_pretty


def is_instance_of_attrs_class(value):
    cls = type(value)

    try:
        cls.__attrs_attrs__
    except AttributeError:
        return False

    return True


def pretty_attrs(value, ctx):
    cls = type(value)
    attributes = cls.__attrs_attrs__

    kwargs = []
    for attribute in attributes:
        display_attr = False
        if attribute.default == NOTHING:
            display_attr = True
        elif isinstance(attribute.default, Factory):
            default_value = (
                attribute.default.factory(value)
                if attribute.default.takes_self
                else attribute.default.factory()
            )
            if default_value != getattr(value, attribute.name):
                display_attr = True
        else:
            if attribute.default != getattr(value, attribute.name):
                display_attr = True

        if display_attr:
            kwargs.append((attribute.name, getattr(value, attribute.name)))

    return pretty_call(ctx, cls, **OrderedDict(kwargs))


def install():
    register_pretty(predicate=is_instance_of_attrs_class)(pretty_attrs)
