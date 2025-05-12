import re

from Mbase.error import print_error_with_origin
from Mbase.types import VALID_DIGITS
from Parser.token_type import TokenType
from Parser.token import Token

def tokenize(source):
    i = 0
    while i < len(source):
        char = source[i]

        # Base literal: b10@123
        if char == 'b':
            base_match = re.match(r"b(\d{1,2})@", source[i:])
            if base_match:
                base = int(base_match.group(1))
                j = i + base_match.end()

                if j < len(source) and source[j] == '(':  # b10@(...)
                    j += 1
                    start = j
                    while j < len(source) and source[j] != ')':
                        j += 1
                    if j == len(source):
                        print_error_with_origin(source, i, "Unclosed base literal", label="SyntaxError")
                        return
                    raw = source[start:j]
                    j += 1
                else:
                    start = j
                    while j < len(source) and source[j].lower() in VALID_DIGITS[:base]:
                        j += 1
                    raw = source[start:j]

                yield Token(TokenType.BASE_LITERAL, (base, raw), i)
                i = j
                continue

        # Skip comments
        if char == '#':
            while i < len(source) and source[i] != '\n':
                i += 1
            continue

        # Newline
        elif char.isspace():
            if char == '\n':
                yield Token(TokenType.NEWLINE, '\n', i)
            i += 1
            continue

        # Multi-character operators
        elif source[i:i+3] == '===':
            yield Token(TokenType.STRICT_EQUAL, '===', i)
            i += 3
        elif source[i:i+3] == '!==':
            yield Token(TokenType.STRICT_NOTEQUAL, '!==', i)
            i += 3
        elif source[i:i+2] == '==':
            yield Token(TokenType.EQUAL, '==', i)
            i += 2
        elif source[i:i+2] == '!=':
            yield Token(TokenType.NOTEQUAL, '!=', i)
            i += 2
        elif source[i:i+2] == '<=':
            yield Token(TokenType.LEQ, '<=', i)
            i += 2
        elif source[i:i+2] == '>=':
            yield Token(TokenType.GEQ, '>=', i)
            i += 2
        elif source[i:i+2] == '&&':
            yield Token(TokenType.AND, '&&', i)
            i += 2
        elif source[i:i+2] == '||':
            yield Token(TokenType.OR, '||', i)
            i += 2

        # Single-character symbols
        elif char == ';':
            yield Token(TokenType.SEMICOLON, ';', i); i += 1
        elif char == ',':
            yield Token(TokenType.COMMA, ',', i); i += 1
        elif char == '{':
            yield Token(TokenType.LBRACE, '{', i); i += 1
        elif char == '}':
            yield Token(TokenType.RBRACE, '}', i); i += 1
        elif char == '(':
            yield Token(TokenType.LPAREN, '(', i); i += 1
        elif char == ')':
            yield Token(TokenType.RPAREN, ')', i); i += 1
        elif char == '=':
            yield Token(TokenType.ASSIGN, '=', i); i += 1
        elif char == '+':
            yield Token(TokenType.PLUS, '+', i); i += 1
        elif char == '-':
            yield Token(TokenType.MINUS, '-', i); i += 1
        elif char == '*':
            yield Token(TokenType.STAR, '*', i); i += 1
        elif char == '/':
            yield Token(TokenType.SLASH, '/', i); i += 1
        elif char == '<':
            yield Token(TokenType.LESSTHAN, '<', i); i += 1
        elif char == '>':
            yield Token(TokenType.GREATERTHAN, '>', i); i += 1
        elif char == '!':
            yield Token(TokenType.NOT, '!', i); i += 1
        elif char == '@':
            yield Token(TokenType.AT, '@', i); i += 1

        # String literals
        elif char == '"':
            start = i
            i += 1
            content = ''
            while i < len(source):
                if source[i] == '\\' and i + 1 < len(source):
                    esc = source[i+1]
                    content += {'n':'\n','t':'\t','"':'"','\\':'\\'}.get(esc, esc)
                    i += 2
                elif source[i] == '"':
                    i += 1
                    break
                else:
                    content += source[i]
                    i += 1
            yield Token(TokenType.TEXT, content, start)

        # Numbers
        elif re.match(r'[0-9]', char):
            start = i
            while i < len(source) and source[i].isdigit():
                i += 1
            yield Token(TokenType.NUMBER, source[start:i], start)

        # Identifiers and keywords
        elif re.match(r'[a-zA-Z_]', char):
            start = i
            while i < len(source) and re.match(r'[a-zA-Z0-9_]', source[i]):
                i += 1
            value = source[start:i]
            type_map = {
                "fn": TokenType.FUNCTION,
                "ret": TokenType.RETURN,
                "if": TokenType.IF,
                "else": TokenType.ELSE,
                "while": TokenType.WHILE,
                "loop": TokenType.LOOP,
                "break": TokenType.BREAK,
                "continue": TokenType.CONTINUE,
            }
            tok_type = type_map.get(value, TokenType.IDENTIFIER)
            yield Token(tok_type, value, start)

        # Error for unknown chars
        else:
            print_error_with_origin(source, i, f"Unexpected character: {char}", label="SyntaxError")
            raise SyntaxError(f"Unexpected character: {char}")

    yield Token(TokenType.EOF, None, len(source))
