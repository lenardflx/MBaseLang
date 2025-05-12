from Mbase.types import BaseLiteral, Function
import time

def builtin_out(value: str):
    print(value, end="")

def builtin_in() -> str:
    return input()

def builtin_wait(n):
    if isinstance(n, BaseLiteral):
        n = n.to_int()
    time.sleep(n)

def builtin_len(value):
    return BaseLiteral(10, str(len(value)))

def builtin_num_len(value):
    return BaseLiteral(10, str(len(value.raw)))

def builtin_str(value):
    return str(value)

def builtin_str_baseless(value):
    return str(value.raw)

def builtin_padstr(value, length):
    l = length.to_int()
    return value.zfill(l)

def builtin_sqrt(value: BaseLiteral):
    val = value.to_int()
    result = int(val ** 0.5)
    return BaseLiteral.from_int(value.base, result)

def builtin_number(value: str, base=10):
    return BaseLiteral(base, value)

def builtin_rebase(value: BaseLiteral, new_base: BaseLiteral):
    try:
        base_int = new_base.to_int()
    except ValueError:
        raise ValueError(f"rebase: invalid base value '{new_base.raw}'")

    if base_int < 2 or base_int > 64:
        raise ValueError(f"rebase: target base must be between 2 and 64, got {base_int}")

    return value.rebase(base_int)

BUILTINS = {
    "out": Function(
        name="out",
        args=[("str", "text")],
        return_type=None,
        builtin=True,
        impl=builtin_out
    ),
    "in": Function(
        name="in",
        args=[],
        return_type="str",
        builtin=True,
        impl=builtin_in
    ),
    "wait": Function(
        name="wait",
        args=[("b10", "seconds")],
        return_type=None,
        builtin=True,
        impl=builtin_wait
    ),
    "len": Function(
        name="len",
        args=[("str", "text")],
        return_type="b10",
        builtin=True,
        impl=builtin_len
    ),
    "num_len": Function(
        name="num_len",
        args=[("b_", "val")],
        return_type="b10",
        builtin=True,
        impl=builtin_num_len
    ),
    "str": Function(
        name="str",
        args=[("b_", "val")],
        return_type="str",
        builtin=True,
        impl=builtin_str
    ),
    "str_baseless": Function(
        name="str_baseless",
        args=[("b_", "val")],
        return_type="str",
        builtin=True,
        impl=builtin_str_baseless
    ),
    "padstr": Function(
        name="padstr",
        args=[("str", "text"), ("b10", "length")],
        return_type="str",
        builtin=True,
        impl=builtin_padstr
    ),
    "sqrt": Function(
        name="sqrt",
        args=[("b_", "val")],
        return_type="b_",
        builtin=True,
        impl=builtin_sqrt
    ),
    "number": Function(
        name="number",
        args=[("str", "raw")],
        return_type="b10",
        builtin=True,
        impl=lambda s: BaseLiteral(10, s)
    ),
    "funcs": Function(
        name="funcs",
        args=[],
        return_type=None,
        builtin=True,
        impl=lambda: print("Available functions: " + ", ".join(BUILTINS.keys()))
    ),
    "rebase": Function(
        name="rebase",
        args=[("b_", "val"), ("b_", "base")],
        return_type="b_",
        builtin=True,
        impl=builtin_rebase
    ),
}
