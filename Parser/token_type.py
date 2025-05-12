from enum import Enum, auto

class TokenType(Enum):
    # Literals & Identifiers
    IDENTIFIER = auto()
    NUMBER = auto()
    BASE_LITERAL = auto()
    TEXT = auto()

    # Grouping
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    LBRACE = auto()       # {
    RBRACE = auto()       # }

    # Arithmetic Operators
    PLUS = auto()         # +
    MINUS = auto()        # -
    STAR = auto()         # *
    SLASH = auto()        # /

    # Comparison Operators
    ASSIGN = auto()       # =
    EQUAL = auto()        # ==
    STRICT_EQUAL = auto() # ===
    NOTEQUAL = auto()     # !=
    STRICT_NOTEQUAL = auto() # !==
    LESSTHAN = auto()     # <
    LEQ = auto()          # <=
    GREATERTHAN = auto()  # >
    GEQ = auto()          # >=

    # Logical Operators
    AND = auto()          # &&
    OR = auto()           # ||
    NOT = auto()          # !

    # Control Flow
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    LOOP = auto()
    BREAK = auto()
    CONTINUE = auto()

    # Other Punctuation
    SEMICOLON = auto()    # ;
    COMMA = auto()        # ,
    AT = auto()           # @

    # Misc
    RETURN = auto()
    FUNCTION = auto()
    COMMENT = auto() # wont be used, tokenizer ignores "#"
    NEWLINE = auto()
    EOF = auto()
