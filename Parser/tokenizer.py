import re

from Mbase.error import print_error_with_origin
from Mbase.types import VALID_DIGITS
from Parser.token_type import TokenType
from Parser.token import Token

def tokenize(source):
    i = 0
    while i < len(source):
        char = source[i]

        if char == 'b':
            base_match = re.match(r"b(\d{1,2})@", source[i:])
            if base_match:
                base = int(base_match.group(1))
                j = i + base_match.end()  # after 'b10@'

                if j < len(source) and source[j] == '(':  # b64@(...)
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
                    while j < len(source):
                        ch = source[j].lower()
                        if ch not in VALID_DIGITS[:base]:
                            break
                        j += 1
                    raw = source[start:j]

                yield Token(TokenType.BASE_LITERAL, (base, raw), i)
                i = j
                continue

        if char == '#':
            while i < len(source) and source[i] != '\n':
                i += 1
            continue
        elif char.isspace():
            if char == '\n':
                yield Token(TokenType.NEWLINE, '\n', i)
            i += 1
            continue
        elif char == ';':
            yield Token(TokenType.SEMICOLON, ';', i)
            i += 1
        elif char == ',':
            yield Token(TokenType.COMMA, ',', i)
            i += 1
        elif char == '{':
            yield Token(TokenType.LBRACE, '{', i)
            i += 1
        elif char == '}':
            yield Token(TokenType.RBRACE, '}', i)
            i += 1
        elif char == '=':
            yield Token(TokenType.ASSIGN, '=', i)
            i += 1
        elif char == '+':
            yield Token(TokenType.PLUS, '+', i)
            i += 1
        elif char == '-':
            yield Token(TokenType.MINUS, '-', i)
            i += 1
        elif char == '*':
            yield Token(TokenType.STAR, '*', i)
            i += 1
        elif char == '/':
            yield Token(TokenType.SLASH, '/', i)
            i += 1
        elif char == '(':
            yield Token(TokenType.LPAREN, '(', i)
            i += 1
        elif char == ')':
            yield Token(TokenType.RPAREN, ')', i)
            i += 1
        elif char == '"':
            start = i
            i += 1
            content = ''
            while i < len(source):
                if source[i] == '\\' and i + 1 < len(source):
                    esc = source[i + 1]
                    if esc == 'n':
                        content += '\n'
                    elif esc == 't':
                        content += '\t'
                    elif esc == '"':
                        content += '"'
                    elif esc == '\\':
                        content += '\\'
                    else:
                        content += esc
                    i += 2
                elif source[i] == '"':
                    i += 1
                    break
                else:
                    content += source[i]
                    i += 1
            yield Token(TokenType.TEXT, content, start)
        elif re.match(r'[0-9]', char):
            start = i
            while i < len(source) and source[i].isdigit():
                i += 1
            yield Token(TokenType.NUMBER, source[start:i], start)
        elif re.match(r'[a-zA-Z_]', char):
            start = i
            while i < len(source) and re.match(r'[a-zA-Z0-9_]', source[i]):
                i += 1
            value = source[start:i]
            type_map = {
                "fn": TokenType.FUNCTION,
                "ret": TokenType.RETURN,
            }
            tok_type = type_map.get(value, TokenType.IDENTIFIER)
            yield Token(tok_type, value, start)
        else:
            print_error_with_origin(source, i, f"Unexpected character: {char}", label="SyntaxError")
            raise SyntaxError(f"Unexpected character: {char}")

    yield Token(TokenType.EOF, None, len(source))
