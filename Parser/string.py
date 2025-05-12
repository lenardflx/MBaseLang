from Mbase.error import print_error_with_origin
from Parser.parse import Parser
from Parser.tokenizer import tokenize


def extract_string_parts(inner: str, start_idx=0):
    parts = []
    i = 0
    buffer = ""
    while i < len(inner):
        if inner[i] == '\\' and i + 1 < len(inner):
            buffer += inner[i + 1]
            i += 2
        elif inner[i] == '{':
            if buffer:
                parts.append(buffer)
                buffer = ""
            j = i + 1
            while j < len(inner) and inner[j] != '}':
                j += 1
            if j == len(inner):
                print_error_with_origin(inner, start_idx + i, "Unclosed '{' in string", label="SyntaxError")
                return None
            expr_str = inner[i + 1:j].strip()
            try:
                tokens = list(tokenize(expr_str))
                ast = Parser(tokens).parse()
                if len(ast) != 1:
                    raise SyntaxError("Expected one expression inside '{}'")
                parts.append(ast[0])
            except Exception as e:
                print_error_with_origin(inner, start_idx + i, str(e), label="SyntaxError")
                return None
            i = j + 1
        else:
            buffer += inner[i]
            i += 1
    if buffer:
        parts.append(buffer)
    return parts