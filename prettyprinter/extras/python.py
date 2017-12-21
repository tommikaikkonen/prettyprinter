import builtins
import sys
from io import StringIO

from prettyprinter import cpprint
from prettyprinter.utils import get_terminal_width


def install():
    try:
        get_ipython
    except NameError:
        pass
    else:
        raise ValueError(
            "Don't install the default Python shell integration "
            "if you're using IPython, use the IPython integration with "
            "prettyprinter.install_extras(include=['ipython'])."
        )

    def prettyprinter_displayhook(value):
        if value is None:
            return

        builtins._ = None
        stream = StringIO()
        output = cpprint(
            value,
            width=get_terminal_width(default=79),
            stream=stream,
            end=''
        )
        output = stream.getvalue()

        try:
            sys.stdout.write(output)
        except UnicodeEncodeError:
            encoded = output.encode(sys.stdout.encoding, 'backslashreplace')
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout.buffer.write(encoded)
            else:
                text = encoded.decode(sys.stdout.encoding, 'strict')
                sys.stdout.write(text)

        sys.stdout.write('\n')
        builtins._ = value

    sys.displayhook = prettyprinter_displayhook
