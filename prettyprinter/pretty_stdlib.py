from collections import (
    ChainMap,
    Counter,
    OrderedDict,
    defaultdict,
    deque,
)
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
    pretty_call_alt,
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
    return pretty_call_alt(ctx, type(value), args=(str(value), ))


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

    # Doesn't exist before Python 3.6
    if getattr(dt, 'fold', None):
        kwargs.append(('fold', 1))

    if len(kwargs) == 3:  # year, month, day
        return pretty_call_alt(
            ctx,
            datetime,
            args=(
                dt.year,
                dt.month,
                dt.day
            )
        )

    return pretty_call_alt(ctx, datetime, kwargs=kwargs)


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
        return pretty_call_alt(ctx, timezone, args=(tz._offset, ))
    return pretty_call_alt(ctx, timezone, args=(tz._offset, tz._name))


def pretty_pytz_timezone(tz, ctx):
    if tz == pytz.utc:
        return identifier('pytz.utc')
    return pretty_call_alt(ctx, pytz.timezone, args=(tz.zone, ))


def pretty_pytz_dst_timezone(tz, ctx):
    if tz.zone and pytz.timezone(tz.zone) == tz:
        return pretty_pytz_timezone(tz, ctx)

    calldoc = pretty_call_alt(
        ctx,
        pytz.tzinfo.DstTzInfo,
        args=((tz._utcoffset, tz._dst, tz._tzname), )
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

    if getattr(value, 'fold', 0) != 0:
        additional_kws.append(('fold', value.fold))

    kwargs = chain(
        (
            (kw, getattr(value, kw))
            for kw in timekws_to_display
        ),
        additional_kws
    )

    return pretty_call_alt(
        ctx,
        time,
        kwargs=kwargs
    )


@register_pretty(date)
def pretty_date(value, ctx):
    return pretty_call_alt(
        ctx,
        date,
        args=(value.year, value.month, value.day)
    )


@register_pretty(timedelta)
def pretty_timedelta(delta, ctx):
    if ctx.depth_left == 0:
        return pretty_call_alt(ctx, timedelta, args=(..., ))

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


@register_pretty(ChainMap)
def pretty_chainmap(value, ctx):
    constructor = type(value)
    if (
        not value.maps or
        len(value.maps) == 1 and
        not value.maps[0]
    ):
        return pretty_call_alt(ctx, constructor)

    return pretty_call_alt(ctx, constructor, args=value.maps)


@register_pretty(defaultdict)
def pretty_defaultdict(d, ctx):
    constructor = type(d)
    return pretty_call_alt(
        ctx,
        constructor,
        args=(d.default_factory, dict(d))
    )


@register_pretty(deque)
def pretty_deque(value, ctx):
    kwargs = []
    if value.maxlen is not None:
        kwargs.append(('maxlen', value.maxlen))

    return pretty_call_alt(
        ctx,
        type(value),
        args=(list(value), ),
        kwargs=kwargs
    )


@register_pretty(OrderedDict)
def pretty_ordereddict(d, ctx):
    return pretty_call_alt(ctx, type(d), args=(list(d.items()), ))


@register_pretty(Counter)
def pretty_counter(counter, ctx):
    return pretty_call_alt(ctx, type(counter), args=(dict(counter), ))


@register_pretty('enum.Enum')
def pretty_enum(value, ctx):
    cls = type(value)
    return classattr(cls, value.name)


@register_pretty('builtins.mappingproxy')
def pretty_mappingproxy(value, ctx):
    return pretty_call_alt(ctx, type(value), args=(dict(value), ))


@register_pretty('functools.partial')
def pretty_partial(value, ctx):
    constructor = type(value)
    return pretty_call_alt(
        ctx,
        constructor,
        args=(value.func, ) + value.args,
        kwargs=value.keywords
    )


@register_pretty(BaseException)
def pretty_baseexception(exc, ctx):
    return pretty_call_alt(
        ctx,
        type(exc),
        args=exc.args
    )


@register_pretty('_ast.AST')
def pretty_nodes(value, ctx):
    cls = type(value)
    kwargs = [(k, getattr(value, k, None)) for k in value._fields]
    if cls.__module__ == '_ast':
        cls_name = 'ast.%s' % cls.__qualname__
    else:
        cls_name = cls
    return pretty_call_alt(ctx, cls_name, kwargs=kwargs)


@register_pretty('pathlib.PurePath')
def pretty_pathlib(value, ctx):
    return pretty_call_alt(ctx, type(value), args=(value.as_posix(),))


@register_pretty('_io.TextIOWrapper')
def pretty_fp(value, ctx):
    cls = 'FP'
    fields = [('mode', 'r'), ('encoding', None),
              ('buffer', None), ('closed', None)]
    mode_definition = {
        'r': 'open for reading(default)',
        'w': 'open for writing, truncating the file first',
        'x': 'open for exclusive creation, failing if the file already exists',
        'a': 'open for writing, appending to the end of the file if it exists',
        'b': 'binary mode',
        't': 'text mode(default)',
        '+': 'open a disk file for updating(reading and writing)',
        'U': 'universal newlines mode(deprecated) ',
    }
    kwargs = dict([(k, getattr(value, k, default)) for k, default in fields])
    kwargs['path'] = kwargs['buffer'].name
    kwargs['modes'] = '\n'.join([mode_definition[k] for k in kwargs['mode']])
    del kwargs['buffer']
    del kwargs['mode']
    return pretty_call_alt(ctx, cls, kwargs=kwargs)
