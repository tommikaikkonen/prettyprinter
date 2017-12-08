from io import StringIO

from .sdoctypes import SLine
from .utils import rfind_idx


def as_lines(sdocs):
    it = iter(sdocs)
    currline = []
    for sdoc in it:
        if not isinstance(sdoc, SLine):
            currline.append(sdoc)
        else:
            yield currline
            currline = [sdoc]

    if currline:
        yield currline


def default_render_to_stream(stream, sdocs, newline='\n', separator=' '):
    evald = list(sdocs)

    if not evald:
        return

    for sdoc_line in as_lines(evald):
        last_text_sdoc_idx = rfind_idx(
            lambda sdoc: isinstance(sdoc, str),
            sdoc_line
        )

        # Edge case: trailing whitespace on a line.
        # Currently happens on multiline str value in a dict:
        # there's a trailing whitespace after the colon that's
        # hard to eliminate at the doc level.
        if last_text_sdoc_idx != -1:
            last_text_sdoc = sdoc_line[last_text_sdoc_idx]
            sdoc_line[last_text_sdoc_idx] = last_text_sdoc.rstrip()

        for sdoc in sdoc_line:
            if isinstance(sdoc, str):
                stream.write(sdoc)
            elif isinstance(sdoc, SLine):
                stream.write(newline + separator * sdoc.indent)


def default_render_to_str(sdocs, newline='\n', separator=' '):
    stream = StringIO()
    default_render_to_stream(stream, sdocs, newline, separator)
    return stream.getvalue()
