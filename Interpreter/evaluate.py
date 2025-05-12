from Mbase.error import print_error_with_origin
from Mbase.types import BaseLiteral, Function
from Parser.token_type import TokenType
from Parser.string import extract_string_parts
from Parser.token import Token

class BreakSignal(Exception):
    def __init__(self, label=None):
        self.label = label

class ContinueSignal(Exception):
    def __init__(self, label=None):
        self.label = label

def evaluate(expr, ctx):
    if isinstance(expr, BaseLiteral):
        return expr
    elif isinstance(expr, Function):
        ctx.setdefault("__functions__", {})[expr.name] = expr
        return None
    elif isinstance(expr, int):
        return expr
    elif isinstance(expr, str):
        return expr

    elif isinstance(expr, tuple):
        tag = expr[0]

        if tag == "var":
            name = expr[1]
            if name not in ctx:
                raise NameError(f"Undefined variable '{name}'")
            return ctx[name]

        elif tag == "assign":
            _, name, value_expr = expr
            value = evaluate(value_expr, ctx)
            ctx[name] = value
            return None

        elif tag == "binop":
            op = expr[1]
            left = expr[2]
            right = expr[3]
            pos = expr[4] if len(expr) > 4 else None

            try:
                if op == TokenType.PLUS:
                    return evaluate(left, ctx) + evaluate(right, ctx)
                elif op == TokenType.MINUS:
                    return evaluate(left, ctx) - evaluate(right, ctx)
                elif op == TokenType.STAR:
                    return evaluate(left, ctx) * evaluate(right, ctx)
                elif op == TokenType.SLASH:
                    return evaluate(left, ctx) / evaluate(right, ctx)
                elif op == TokenType.EQUAL:
                    return evaluate(left, ctx).to_int() == evaluate(right, ctx).to_int()
                elif op == TokenType.STRICT_EQUAL:
                    return evaluate(left, ctx) == evaluate(right, ctx)
                elif op == TokenType.NOTEQUAL:
                    return evaluate(left, ctx).to_int() != evaluate(right, ctx).to_int()
                elif op == TokenType.STRICT_NOTEQUAL:
                    return evaluate(left, ctx) != evaluate(right, ctx)
                elif op == TokenType.LESSTHAN:
                    return evaluate(left, ctx).to_int() < evaluate(right, ctx).to_int()
                elif op == TokenType.LEQ:
                    return evaluate(left, ctx).to_int() <= evaluate(right, ctx).to_int()
                elif op == TokenType.GREATERTHAN:
                    return evaluate(left, ctx).to_int() > evaluate(right, ctx).to_int()
                elif op == TokenType.GEQ:
                    return evaluate(left, ctx).to_int() >= evaluate(right, ctx).to_int()
                elif op == TokenType.AND:
                    return truthy(evaluate(left, ctx)) and truthy(evaluate(right, ctx))
                elif op == TokenType.OR:
                    return truthy(evaluate(left, ctx)) or truthy(evaluate(right, ctx))
                elif op == TokenType.NOT:
                    return not truthy(evaluate(right, ctx))
                else:
                    raise TypeError(f"Unsupported operator: {op}")
            except Exception as e:
                if pos is not None:
                    print_error_with_origin(ctx.get("__source__", ""), pos, str(e), ctx.get("__filename__", "<input>"))
                    return None
                else:
                    raise

        elif tag == "call":
            name = expr[1]
            args_exprs = expr[2]
            args = [evaluate(arg, ctx) for arg in args_exprs]

            functions = ctx.get("__functions", ctx.get("__functions__", {}))
            fn = functions.get(name)
            if fn is None:
                raise NameError(f"Unknown function '{name}'")

            if len(args) != len(fn.args):
                raise TypeError(f"'{name}' expects {len(fn.args)} argument(s), got {len(args)}")

            for i, ((expected_type, _), arg) in enumerate(zip(fn.args, args)):
                if expected_type.startswith("b"):
                    if not isinstance(arg, BaseLiteral):
                        raise TypeError(f"Argument {i + 1} must be BaseLiteral")
                    if expected_type != "b_" and arg.base != int(expected_type[1:]):
                        raise TypeError(f"Argument {i + 1} must be base {expected_type[1:]}, got base {arg.base}")
                elif expected_type == "str":
                    if not isinstance(arg, str):
                        raise TypeError(f"Argument {i + 1} must be str, got {type(arg).__name__}")
                else:
                    raise TypeError(f"Unknown expected type '{expected_type}'")

            if fn.builtin:
                return fn.impl(*args)

            local_ctx = ctx.copy()
            for (_, var), val in zip(fn.args, args):
                local_ctx[var] = val

            result = None
            for stmt in fn.body:
                val = evaluate(stmt, local_ctx)
                if isinstance(stmt, tuple) and stmt[0] == "ret":
                    result = val
                    break

            return result

        elif tag == "ret":
            return evaluate(expr[1], ctx)

        elif tag == "text":
            parts = extract_string_parts(expr[1])
            if parts is None:
                return None
            return evaluate_text(parts, ctx)

        elif tag == "if":
            _, label, cond_expr, then_body, else_body = expr
            if truthy(evaluate(cond_expr, ctx)):
                for stmt in then_body:
                    evaluate(stmt, ctx)
            elif else_body:
                for stmt in else_body:
                    evaluate(stmt, ctx)
            return None

        elif tag in ("while", "loop"):
            label = expr[1]
            cond_expr = expr[2] if tag == "while" else None
            body = expr[3] if tag == "while" else expr[2]

            def loop_body():
                while tag == "loop" or truthy(evaluate(cond_expr, ctx)):
                    try:
                        for stmt_ in body:
                            evaluate(stmt_, ctx)
                    except ContinueSignal as c:
                        if c.label is None or c.label == label:
                            continue
                        raise
                    except BreakSignal as b:
                        if b.label is None or b.label == label:
                            break
                        raise

            loop_body()
            return None

        elif tag == "break":
            raise BreakSignal(expr[1])

        elif tag == "continue":
            raise ContinueSignal(expr[1])

    raise TypeError(f"Unsupported expression type: {expr}")

def evaluate_text(parts, ctx):
    result = ""
    for part in parts:
        if isinstance(part, str):
            result += part
        elif isinstance(part, Token) and part.type == TokenType.IDENTIFIER:
            var = part.value
            if var not in ctx:
                raise NameError(f"Undefined variable in string: '{var}'")
            result += str(evaluate(("var", var), ctx))
        else:
            result += str(evaluate(part, ctx))
    return result

def truthy(value):
    if value is None:
        return False
    if isinstance(value, BaseLiteral):
        return value.to_int() != 0
    if isinstance(value, int):
        return value != 0
    return bool(value)
