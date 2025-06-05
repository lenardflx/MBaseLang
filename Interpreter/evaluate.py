from Mbase.error import print_error_with_origin
from Mbase.types import BaseLiteral, Function
from Parser.token_type import TokenType
from Parser.string import extract_string_parts
from Mbase.ast import (
    Assign,
    BinOp,
    Break,
    Call,
    Continue,
    If,
    Loop,
    Return,
    Text,
    Var,
    While,
)

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

    elif isinstance(expr, Var):
        name = expr.name
        if name not in ctx:
            raise NameError(f"Undefined variable '{name}'")
        return ctx[name]

    elif isinstance(expr, Assign):
        value = evaluate(expr.value, ctx)
        ctx[expr.name] = value
        return None

    elif isinstance(expr, BinOp):
        op = expr.op
        left = expr.left
        right = expr.right
        pos = expr.pos

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
                print_error_with_origin(
                    ctx.get("__source__", ""), pos, str(e), ctx.get("__filename__", "<input>")
                )
                return None
            else:
                raise

    elif isinstance(expr, Call):
        name = expr.name
        args_exprs = expr.args
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
                    raise TypeError(
                        f"Argument {i + 1} must be base {expected_type[1:]}, got base {arg.base}"
                    )
            elif expected_type == "str":
                if not isinstance(arg, str):
                    raise TypeError(
                        f"Argument {i + 1} must be str, got {type(arg).__name__}"
                    )
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
            if isinstance(stmt, Return):
                result = val
                break

        return result

    elif isinstance(expr, Return):
        return evaluate(expr.value, ctx)

    elif isinstance(expr, Text):
        parts = extract_string_parts(expr.value)
        if parts is None:
            return None
        return evaluate_text(parts, ctx)

    elif isinstance(expr, If):
        if truthy(evaluate(expr.condition, ctx)):
            for stmt in expr.then_body:
                evaluate(stmt, ctx)
        elif expr.else_body:
            for stmt in expr.else_body:
                evaluate(stmt, ctx)
        return None

    elif isinstance(expr, While):
        label = expr.label
        cond_expr = expr.condition
        body = expr.body

        while truthy(evaluate(cond_expr, ctx)):
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
        return None

    elif isinstance(expr, Loop):
        label = expr.label
        body = expr.body
        while True:
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
        return None

    elif isinstance(expr, Break):
        raise BreakSignal(expr.label)

    elif isinstance(expr, Continue):
        raise ContinueSignal(expr.label)

    raise TypeError(f"Unsupported expression type: {expr}")

def evaluate_text(parts, ctx):
    result = ""
    for part in parts:
        if isinstance(part, str):
            result += part
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
