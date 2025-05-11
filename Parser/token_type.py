from enum import Enum, auto

class TokenType(Enum):
    IDENTIFIER = auto()
    ASSIGN = auto()
    NUMBER = auto()
    BASE_LITERAL = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    SEMICOLON = auto()
    COMMA = auto()
    TEXT = auto()
    RETURN = auto()
    FUNCTION = auto()
    COMMENT = auto() # wont be used, tokenizer ignores "#"
    NEWLINE = auto()
    EOF = auto()
