from enum import IntEnum, unique


@unique
class Token(IntEnum):
    KEYWORD_CONSTANT = 1
    NAME_BUILTIN = 2
    NAME_ENTITY = 3
    NAME_FUNCTION = 4
    LITERAL_STRING = 5
    STRING_AFFIX = 6
    STRING_ESCAPE = 7
    NUMBER_BINARY = 8
    NUMBER_FLOAT = 9
    NUMBER_INT = 10
    OPERATOR = 11
    PUNCTUATION = 12
    COMMENT_SINGLE = 13
