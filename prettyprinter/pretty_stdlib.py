from collections import Counter, OrderedDict
from datetime import (
    datetime,
    timedelta,
    tzinfo,
    timezone,
    date,
    time,
)
from itertools import chain, dropwhile

from .doc import (
    concat,
    group,
)

from .prettyprinter import (
    ADD_OP,
    MUL_OP,
    NEG_OP,
    comment,
    build_fncall,
    classattr,
    identifier,
    register_pretty,
    pretty_call,
    pretty_python_value,
)

try:
    import pytz
except ImportError:
    _PYTZ_INSTALLED = False
else:
    _PYTZ_INSTALLED = True


@register_pretty('uuid.UUID')
def pretty_uuid(value, ctx):
    return pretty_call(ctx, type(value), str(value))


@register_pretty(datetime)
def pretty_datetime(dt, ctx):
    dt_kwargs = [
        (k, getattr(dt, k))
        for k in (
            'microsecond',
            'second',
            'minute',
            'hour',
            'day',
            'month',
            'year',
        )
    ]

    kwargs = list(reversed(list(
        dropwhile(
            lambda k__v: k__v[1] == 0,
            dt_kwargs
        )
    )))

    if dt.tzinfo is not None:
        kwargs.append(('tzinfo', dt.tzinfo))

    if dt.fold:
        kwargs.append(('fold', 1))

    if len(kwargs) == 3:  # year, month, day
        return pretty_call(
            ctx,
            datetime,
            dt.year,
            dt.month,
            dt.day,
        )

    return pretty_call(ctx, datetime, **OrderedDict(kwargs))


@register_pretty(tzinfo)
def pretty_tzinfo(value, ctx):
    if value == timezone.utc:
        return identifier('datetime.timezone.utc')
    elif _PYTZ_INSTALLED and value == pytz.utc:
        return identifier('pytz.utc')
    else:
        return repr(value)


@register_pretty(timezone)
def pretty_timezone(tz, ctx):
    if tz == timezone.utc:
        return identifier('datetime.timezone.utc')

    if tz._name is None:
        return pretty_call(ctx, timezone, tz._offset)
    return pretty_call(ctx, timezone, tz._offset, tz._name)


def pretty_pytz_timezone(tz, ctx):
    if tz == pytz.utc:
        return identifier('pytz.utc')
    return pretty_call(ctx, pytz.timezone, tz.zone)


def pretty_pytz_dst_timezone(tz, ctx):
    if tz.zone and pytz.timezone(tz.zone) == tz:
        return pretty_pytz_timezone(tz, ctx)

    calldoc = pretty_call(
        ctx,
        pytz.tzinfo.DstTzInfo,
        (tz._utcoffset, tz._dst, tz._tzname)
    )

    if tz.zone:
        return comment(
            calldoc,
            'In timezone {}'.format(tz.zone)
        )
    return calldoc


if _PYTZ_INSTALLED:
    register_pretty(pytz.tzinfo.BaseTzInfo)(pretty_pytz_timezone)
    register_pretty(pytz.tzinfo.DstTzInfo)(pretty_pytz_dst_timezone)


@register_pretty(time)
def pretty_time(value, ctx):
    timekws_to_display = reversed(
        list(
            dropwhile(
                lambda kw: getattr(value, kw) == 0,
                ('microsecond', 'second', 'minute', 'hour')
            )
        )
    )

    additional_kws = []
    if value.tzinfo is not None:
        additional_kws.append(('tzinfo', value.tzinfo))

    if value.fold != 0:
        additional_kws.append(('fold', value.fold))

    kwargs = chain(
        (
            (kw, getattr(value, kw))
            for kw in timekws_to_display
        ),
        additional_kws
    )

    return pretty_call(
        ctx,
        time,
        **OrderedDict(kwargs)
    )


@register_pretty(date)
def pretty_date(value, ctx):
    return pretty_call(ctx, date, value.year, value.month, value.day)


@register_pretty(timedelta)
def pretty_timedelta(delta, ctx):
    if ctx.depth_left == 0:
        return pretty_call(ctx, timedelta, ...)

    pos_delta = abs(delta)
    negative = delta != pos_delta

    days = pos_delta.days
    seconds = pos_delta.seconds
    microseconds = pos_delta.microseconds

    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    milliseconds, microseconds = divmod(microseconds, 1000)

    attrs = [
        ('days', days),
        ('hours', hours),
        ('minutes', minutes),
        ('seconds', seconds),
        ('milliseconds', milliseconds),
        ('microseconds', microseconds),
    ]

    kwargdocs = [
        (k, pretty_python_value(v, ctx=ctx.nested_call()))
        for k, v in attrs
        if v != 0
    ]

    if kwargdocs and kwargdocs[0][0] == 'days':
        years, days = divmod(days, 365)
        if years:
            _docs = []

            if years > 1:
                _docs.extend([
                    pretty_python_value(years, ctx),
                    ' ',
                    MUL_OP,
                    ' '
                ])

            _docs.append(pretty_python_value(365, ctx))

            if days:
                _docs.extend([
                    ' ',
                    ADD_OP,
                    ' ',
                    pretty_python_value(days, ctx)
                ])

            kwargdocs[0] = ('days', concat(_docs))

    doc = group(
        build_fncall(
            ctx,
            timedelta,
            kwargdocs=kwargdocs,
        )
    )

    if negative:
        doc = concat([NEG_OP, doc])

    return doc


@register_pretty(OrderedDict)
def pretty_ordereddict(d, ctx):
    return pretty_call(ctx, type(d), [*d.items()])


@register_pretty(Counter)
def pretty_counter(counter, ctx):
    return pretty_call(ctx, type(counter), dict(counter))


@register_pretty('enum.Enum')
def pretty_enum(value, ctx):
    cls = type(value)
    return classattr(cls, value.name)


@register_pretty('types.MappingProxyType')
def pretty_mappingproxy(value, ctx):
    return pretty_call(ctx, type(value), dict(value))
