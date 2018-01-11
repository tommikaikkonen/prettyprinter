import os
from pygments.styles import get_style_by_name
from pygments.style import Style

import IPython.lib.pretty
from IPython.lib.pretty import RepresentationPrinter

from .. import cpprint

OriginalRepresentationPrinter = RepresentationPrinter


class _NoStyle(Style):
    pass


# This function mostly mirrors IPython's
# TerminalInteractiveShell._make_style_from_name_or_cls,
# except for style overrides.
# https://github.com/ipython/ipython/blob/5b2b7dd07a268baceeeedfe919de0a59e5bc922b/IPython/terminal/interactiveshell.py#L284-L346
# TODO: support style overrides.
def pygments_style_from_name_or_cls(name_or_cls, ishell):
    if name_or_cls == 'legacy':
        legacy = ishell.colors.lower()
        if legacy == 'linux':
            return get_style_by_name('monokai')
        elif legacy == 'lightbg':
            return get_style_by_name('pastie')
        elif legacy == 'neutral':
            return get_style_by_name('default')
        elif legacy == 'nocolor':
            return _NoStyle
        else:
            raise ValueError('Got unknown colors: ', legacy)
    else:
        if isinstance(name_or_cls, str):
            return get_style_by_name(name_or_cls)
        else:
            return name_or_cls


def install():
    ipy = get_ipython()  # noqa

    try:
        _rows, columns = os.popen('stty size', 'r').read().split()
        columns = int(columns)
    except:  # noqa
        columns = 79

    class IPythonCompatPrinter:
        def __init__(self, stream, *args, **kwargs):
            self.stream = stream

        def pretty(self, obj):
            cpprint(
                obj,
                stream=self.stream,
                style=pygments_style_from_name_or_cls(
                    ipy.highlighting_style,
                    ishell=ipy
                ),
                width=columns,
                end=None
            )

        def flush(self):
            pass

    IPython.lib.pretty.RepresentationPrinter = IPythonCompatPrinter
