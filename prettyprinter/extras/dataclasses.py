from collections import OrderedDict
from dataclasses import (
    fields,
    MISSING,
)

from prettyprinter.prettyprinter import pretty_call, register_pretty


def is_instance_of_dataclass(value):
    try:
        fields(value)
    except TypeError:
        return False
    else:
        return True


def pretty_dataclass_instance(value, ctx):
    cls = type(value)
    field_defs = fields(value)

    kwargs = []
    for field_def in field_defs:
        # repr is True by default,
        # therefore if this if False, the user
        # has explicitly indicated they don't want
        # to display the field value.
        if not field_def.repr:
            continue
        kwargs.append((field_def.name, getattr(value, field_def.name)))

    return pretty_call(ctx, cls, **OrderedDict(kwargs))


def install():
    register_pretty(predicate=is_instance_of_dataclass)(pretty_dataclass_instance)
