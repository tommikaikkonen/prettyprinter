import os
import colorful
from pygments import token, styles
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Text, \
     Number, Operator, Generic, Whitespace, Punctuation, Other, Literal

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
    Token.NAME_VARIABLE: token.Name.Variable,
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


# From https://github.com/primer/github-syntax-theme-generator/blob/master/lib/themes/light.json
# GitHub has MIT licenesed the theme, see
# https://github.com/primer/github-syntax-theme-generator/blob/master/LICENSE
class GitHubLightStyle(Style):
    background_color = "#ffffff"  # done
    highlight_color = "#fafbfc"  # done

    styles = {
        # No corresponding class for the following:
        Text:                      "#24292e",
        Whitespace:                "",
        Error:                     "bold #b31d28",
        Other:                     "",

        Comment:                   "#6a737d",  # done
        Comment.Multiline:         "",
        Comment.Preproc:           "",
        Comment.Single:            "",
        Comment.Special:           "",

        Keyword:                   "#d73a49", # class: 'k'
        Keyword.Constant:          "#005cc5",  # done
        Keyword.Declaration:       "#d73a49",
        Keyword.Namespace:         "#d73a49",
        Keyword.Pseudo:            "",
        Keyword.Reserved:          "",
        Keyword.Type:              "",

        Operator:                  "#d73a49", # class: 'o'
        Operator.Word:             "",        # class: 'ow' - like keywords

        Punctuation:               "", # class: 'p'

        Name:                      "#6f42c1", # class: 'n'
        Name.Attribute:            "#24292e", # class: 'na' - to be revised
        Name.Builtin:              "#005cc5",        # class: 'nb'
        Name.Builtin.Pseudo:       "#005cc5",        # class: 'bp'
        Name.Class:                "#6f42c1", # class: 'nc' - to be revised
        Name.Constant:             "#005cc5", # class: 'no' - to be revised
        Name.Decorator:            "#6f42c1", # done
        Name.Entity:               "#6f42c1",        # done
        Name.Exception:            "#005cc5", # done
        Name.Function:             "#6f42c1", # done
        Name.Function.Magic:       "#005cc5", # done
        Name.Property:             "",        # class: 'py'
        Name.Label:                "",        # class: 'nl'
        Name.Namespace:            "",        # class: 'nn' - to be revised
        Name.Other:                "#005cc5", # class: 'nx'
        Name.Tag:                  "#22863a", # done
        Name.Variable:             "#e36209",        # class: 'nv' - to be revised
        Name.Variable.Class:       "",        # class: 'vc' - to be revised
        Name.Variable.Global:      "",        # class: 'vg' - to be revised
        Name.Variable.Instance:    "",        # class: 'vi' - to be revised

        Number:                    "#005cc5", # class: 'm'
        Number.Float:              "",        # class: 'mf'
        Number.Hex:                "",        # class: 'mh'
        Number.Integer:            "",        # class: 'mi'
        Number.Integer.Long:       "",        # class: 'il'
        Number.Oct:                "",        # class: 'mo'

        Literal:                   "#005cc5", # class: 'l'
        Literal.Date:              "#005cc5", # class: 'ld'

        String:                    "#032f62", # done
        String.Backtick:           "",        # class: 'sb'
        String.Char:               "",        # class: 'sc'
        String.Doc:                "",        # class: 'sd' - like a comment
        String.Double:             "",        # class: 's2'
        String.Escape:             "#22863a", # done
        String.Heredoc:            "",        # class: 'sh'
        String.Interpol:           "#005cc5", # done
        String.Other:              "",        # class: 'sx'
        String.Regex:              "",        # class: 'sr'
        String.Single:             "",        # class: 's1'
        String.Symbol:             "",        # class: 'ss'

        Generic:                   "",        # class: 'g'
        Generic.Deleted:           "#f92672", # class: 'gd',
        Generic.Emph:              "italic",  # class: 'ge'
        Generic.Error:             "",        # class: 'gr'
        Generic.Heading:           "",        # class: 'gh'
        Generic.Inserted:          "#22863a bg: #f0fff4", # class: 'gi'
        Generic.Output:            "",        # class: 'go'
        Generic.Prompt:            "",        # class: 'gp'
        Generic.Strong:            "bold",    # class: 'gs'
        Generic.Subheading:        "bold #005cc5", # class: 'gu'
        Generic.Traceback:         "",        # class: 'gt'
    }


default_dark_style = styles.get_style_by_name('monokai')
default_light_style = GitHubLightStyle

is_light_bg = bool(os.environ.get('PYPRETTYPRINTER_LIGHT_BACKGROUND', False))
default_style = default_light_style if is_light_bg else default_dark_style


def set_default_style(style):
    """Sets default global style to be used by ``prettyprinter.cpprint``.

    :param style: the style to set, either subclass of ``pygments.styles.Style`` or one of ``'dark'``, ``'light'``
    """
    global default_style
    if style == 'dark':
        style = default_dark_style
    elif style == 'light':
        style = default_light_style

    if not issubclass(style, Style):
        raise TypeError(
            "style must be a subclass of pygments.styles.Style or "
            "one of 'dark', 'light'. Got {}".format(repr(style))
        )
    default_style = style


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
