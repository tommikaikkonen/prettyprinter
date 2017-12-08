from enum import IntEnum, auto


class Token(IntEnum):
    KEYWORD_CONSTANT = auto()
    NAME_BUILTIN = auto()
    NAME_ENTITY = auto()
    NAME_FUNCTION = auto()
    LITERAL_STRING = auto()
    STRING_AFFIX = auto()
    STRING_ESCAPE = auto()
    NUMBER_BINARY = auto()
    NUMBER_FLOAT = auto()
    NUMBER_INT = auto()
    OPERATOR = auto()
    PUNCTUATION = auto()
    COMMENT_SINGLE = auto()
