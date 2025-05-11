from Mbase.types import BaseLiteral, Function


def builtin_out(value: str):
    print(value, end="")

def builtin_in() -> str:
    return input()

def builtin_len(value):
    return BaseLiteral(10, str(len(value)))

def builtin_str(value):
    return str(value)

def builtin_sqrt(value: BaseLiteral):
    if value.base == 10:
        val = int(value.raw)
    else:
        val = int(value.raw, value.base)
    result = int(val ** 0.5)
    return BaseLiteral(value.base, format(result, "x" if value.base == 16 else ""))

def builtin_number(value: str, base=10):
    return BaseLiteral(base, value)

def builtin_rebase(value: BaseLiteral, new_base: BaseLiteral):
    try:
        base_int = int(new_base.raw, new_base.base)
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
    "len": Function(
        name="len",
        args=[("str", "text")],
        return_type="b10",
        builtin=True,
        impl=builtin_len
    ),
    "str": Function(
        name="str",
        args=[("b_", "val")],
        return_type="str",
        builtin=True,
        impl=builtin_str
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
