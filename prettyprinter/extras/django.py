from enum import Enum, unique, auto

from django.db.models.fields import NOT_PROVIDED
from django.db.models import Model, ForeignKey
from django.db.models.query import QuerySet

from ..prettyprinter import (
    MULTILINE_STATEGY_HANG,
    build_fncall,
    prettycall,
    pretty_python_value,
    register_pretty,
    annotate_comment,
    trailing_comment
)

from ..utils import find


QUERYSET_OUTPUT_SIZE = 20


@unique
class ModelVerbosity(Enum):
    UNSET = auto()
    MINIMAL = auto()
    SHORT = auto()
    FULL = auto()


def inc(value):
    return value


class dec(object):
    __slots__ = ('value', )

    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        assert isinstance(other, dec)
        return self.value > other.value

    def __gt__(self, other):
        assert isinstance(other, dec)
        return self.value < other.value

    def __eq__(self, other):
        assert isinstance(other, dec)
        return self.value == other.value

    def __le__(self, other):
        assert isinstance(other, dec)
        return self.value >= other.value

    def __ge__(self, other):
        assert isinstance(other, dec)
        return self.value <= other.value

    __hash__ = None


def field_sort_key(field):
    return (
        dec(field.primary_key),
        dec(field.unique),
        inc(field.null),
        inc(field.blank),
        dec(field.default is NOT_PROVIDED),
        inc(field.name),
    )


def pretty_base_model(instance, ctx):
    verbosity = ctx.get(ModelVerbosity)

    model = type(instance)

    if verbosity == ModelVerbosity.MINIMAL:
        fields = [find(lambda field: field.primary_key, model._meta.fields)]
    elif verbosity == ModelVerbosity.SHORT:
        fields = sorted(
            (
                field
                for field in model._meta.fields
                if field.primary_key or not field.null and field.unique
            ),
            key=field_sort_key
        )
    else:
        fields = sorted(model._meta.fields, key=field_sort_key)

    attrs = []
    value_ctx = (
        ctx
        .nested_call()
        .use_multiline_strategy(MULTILINE_STATEGY_HANG)
    )

    null_fieldnames = []
    blank_fieldnames = []
    default_fieldnames = []

    for field in fields:
        if isinstance(field, ForeignKey):
            fk_value = getattr(instance, field.attname)
            if fk_value is not None:
                related_field = field.target_field
                related_model = related_field.model
                attrs.append((
                    field.name,
                    prettycall(
                        ctx,
                        related_model,
                        **{related_field.name: fk_value}
                    )
                ))
            else:
                null_fieldnames.append(field.attname)
        else:
            value = getattr(instance, field.name)

            if field.default is not NOT_PROVIDED:
                if callable(field.default):
                    default_value = field.default()
                else:
                    default_value = field.default

                if value == default_value:
                    default_fieldnames.append(field.attname)
                    continue

            if field.null and value is None:
                null_fieldnames.append(field.attname)
                continue

            if field.blank and value in field.empty_values:
                blank_fieldnames.append(field.attname)
                continue

            kw = field.name
            vdoc = pretty_python_value(value, value_ctx)

            if field.choices:
                choices = tuple(field.choices)
                ungrouped_choices = (
                    (_value, _display)
                    for value, display in choices
                    for _value, _display in (
                        display if
                        isinstance(display, tuple)
                        else [(value, display)])
                )

                value__display = find(
                    lambda value__display: value__display[0],
                    ungrouped_choices,
                )

                try:
                    _, display = value__display
                except ValueError:
                    display = None

                if display:
                    vdoc = annotate_comment(
                        display,
                        vdoc
                    )

            attrs.append((kw, vdoc))

    commentstr = (
        (
            "Null fields: {}\n".format(
                ', '.join(null_fieldnames)
            )
            if null_fieldnames
            else ''
        ) +
        (
            "Blank fields: {}\n".format(
                ', '.join(blank_fieldnames)
            )
            if blank_fieldnames
            else ''
        ) +
        (
            "Default value fields: {}\n".format(
                ', '.join(default_fieldnames)
            )
            if default_fieldnames
            else ''
        )
    )

    return build_fncall(
        ctx,
        model,
        kwargdocs=attrs,
        trailing_comment=commentstr or None,
    )


def pretty_queryset(queryset, ctx):
    qs_cls = type(queryset)

    instances = list(queryset[:QUERYSET_OUTPUT_SIZE + 1])
    if len(instances) > QUERYSET_OUTPUT_SIZE:
        truncated = True
        instances = instances[:-1]
    else:
        truncated = False

    element_ctx = ctx.set(ModelVerbosity, ModelVerbosity.SHORT)

    return prettycall(
        element_ctx,
        qs_cls,
        (
            trailing_comment(
                '...remaining elements truncated',
                instances
            )
            if truncated
            else instances
        )
    )


def install():
    register_pretty(Model)(pretty_base_model)
    register_pretty(QuerySet)(pretty_queryset)
