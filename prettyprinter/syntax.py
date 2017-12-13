from enum import IntEnum, unique


@unique
class Token(IntEnum):
    KEYWORD_CONSTANT = 1
    NAME_BUILTIN = 2
    NAME_ENTITY = 3
    NAME_FUNCTION = 4
    NAME_VARIABLE = 5
    LITERAL_STRING = 6
    STRING_AFFIX = 7
    STRING_ESCAPE = 8
    NUMBER_BINARY = 9
    NUMBER_FLOAT = 10
    NUMBER_INT = 11
    OPERATOR = 12
    PUNCTUATION = 13
    COMMENT_SINGLE = 14
