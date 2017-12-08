import os

import IPython.lib.pretty

from .. import cpprint


def install():
    ipy = get_ipython()  # noqa

    try:
        _rows, columns = os.popen('stty size', 'r').read().split()
        columns = int(columns)
    except:
        columns = 79

    class IPythonCompatPrinter:
        def __init__(self, stream, *args, **kwargs):
            self.stream = stream

        def pretty(self, obj):
            style = ipy.highlighting_style
            if style == 'legacy':
                # Fall back to default
                style = None

            cpprint(obj, stream=self.stream, style=style, width=columns, end=None)

        def flush(self):
            pass

    IPython.lib.pretty.RepresentationPrinter = IPythonCompatPrinter
