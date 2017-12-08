import colorful
from pygments import token, styles

from .sdoctypes import (
    SLine,
    SAnnotationPush,
    SAnnotationPop,
)
from .syntax import Token
from .render import as_lines
from .utils import rfind_idx

_SYNTAX_TOKEN_TO_PYGMENTS_TOKEN = {
    Token.KEYWORD_CONSTANT: token.Keyword.Constant,
    Token.NAME_BUILTIN: token.Name.Builtin,
    Token.NAME_ENTITY: token.Name.Entity,
    Token.NAME_FUNCTION: token.Name.Function,
    Token.LITERAL_STRING: token.String,
    Token.STRING_AFFIX: token.String.Affix,
    Token.STRING_ESCAPE: token.String.Escape,
    Token.NUMBER_INT: token.Number,
    Token.NUMBER_BINARY: token.Number.Bin,
    Token.NUMBER_INT: token.Number.Integer,
    Token.NUMBER_FLOAT: token.Number.Float,
    Token.OPERATOR: token.Operator,
    Token.PUNCTUATION: token.Punctuation,
    Token.COMMENT_SINGLE: token.Comment.Single,
}

default_style = styles.get_style_by_name('monokai')


def styleattrs_to_colorful(attrs):
    c = colorful.reset
    if attrs['color'] or attrs['bgcolor']:
        # Colorful doesn't have a way to directly set Hex/RGB
        # colors- until I find a better way, we do it like this :)
        accessor = ''
        if attrs['color']:
            colorful.update_palette({'prettyprinterCurrFg': attrs['color']})
            accessor = 'prettyprinterCurrFg'
        if attrs['bgcolor']:
            colorful.update_palette({'prettyprinterCurrBg': attrs['bgcolor']})
            accessor += '_on_prettyprinterCurrBg'
        c &= getattr(colorful, accessor)
    if attrs['bold']:
        c &= colorful.bold
    if attrs['italic']:
        c &= colorful.italic
    if attrs['underline']:
        c &= colorful.underline
    return c


def colored_render_to_stream(stream, sdocs, style, newline='\n', separator=' '):
    if style is None:
        style = default_style

    evald = list(sdocs)

    if not evald:
        return

    colorstack = []

    sdoc_lines = as_lines(evald)

    for sdoc_line in sdoc_lines:
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
            elif isinstance(sdoc, SAnnotationPush):
                if isinstance(sdoc.value, Token):
                    pygments_token = _SYNTAX_TOKEN_TO_PYGMENTS_TOKEN[sdoc.value]
                    tokenattrs = style.style_for_token(pygments_token)
                    color = styleattrs_to_colorful(tokenattrs)
                    colorstack.append(color)
                    stream.write(str(color))

            elif isinstance(sdoc, SAnnotationPop):
                try:
                    colorstack.pop()
                except IndexError:
                    continue

                if colorstack:
                    stream.write(str(colorstack[-1]))
                else:
                    stream.write(str(colorful.reset))

    if colorstack:
        stream.write(str(colorful.reset))
