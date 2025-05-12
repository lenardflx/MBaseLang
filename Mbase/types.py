VALID_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/"

class BaseLiteral:
    def __init__(self, base: int, raw: str):
        if not (2 <= base <= 64):
            raise ValueError(f"Base {base} not supported (must be 2–64).")
        self.base = base
        self.raw = raw.lower()
        self._validate()

    def _validate(self):
        allowed = VALID_DIGITS[:self.base]
        for ch in self.raw:
            if ch not in allowed:
                raise ValueError(f"Digit '{ch}' not valid in base {self.base}")

    def to_int(self) -> int:
        digits = VALID_DIGITS[:self.base]
        val = 0
        for ch in self.raw:
            idx = digits.find(ch)
            if idx == -1:
                raise ValueError(f"Invalid digit '{ch}' for base {self.base}")
            val = val * self.base + idx
        return val

    @classmethod
    def from_int(cls, base: int, value: int) -> "BaseLiteral":
        if value < 0:
            raise ValueError("BaseLiteral cannot represent negative values")
        if value == 0:
            return cls(base, "0")
        digits = VALID_DIGITS[:base]
        result = ""
        while value > 0:
            result = digits[value % base] + result
            value //= base
        return cls(base, result)

    def _as_int(self, value):
        if isinstance(value, BaseLiteral):
            return value.to_int()
        elif isinstance(value, int):
            return value
        else:
            raise TypeError(f"Cannot operate with {type(value).__name__}")

    def __add__(self, other):
        result = self.to_int() + self._as_int(other)
        return BaseLiteral.from_int(self.base, result)

    def __sub__(self, other):
        result = self.to_int() - self._as_int(other)
        return BaseLiteral.from_int(self.base, result)

    def __mul__(self, other):
        result = self.to_int() * self._as_int(other)
        return BaseLiteral.from_int(self.base, result)

    def __truediv__(self, other):
        result = self.to_int() // self._as_int(other)
        return BaseLiteral.from_int(self.base, result)

    def __eq__(self, other):
        return isinstance(other, BaseLiteral) and self.base == other.base and self.raw == other.raw

    def __repr__(self):
        return f"BaseLiteral({self.base}, '{self.raw}')"

    def __str__(self):
        if self.base == 10:
            return f"{self.raw}"
        return f"b{self.base}@{self.raw}"

    def as_c_literal(self):
        return f"{self.to_int()} /* b{self.base}@{self.raw} */"

    def rebase(self, target_base):
        return BaseLiteral.from_int(target_base, self.to_int())


class Function:
    def __init__(self, name, args, return_type=None, body=None, builtin=False, impl=None):
        self.name = name
        self.args = args
        self.return_type = return_type
        self.body = body
        self.builtin = builtin
        self.impl = impl

    def is_builtin(self):
        return self.builtin

    def signature(self):
        arg_fmt = ", ".join(f"{t} {n}" for t, n in self.args)
        ret = f" {self.return_type}" if self.return_type else ""
        return f"fn {self.name}({arg_fmt}){ret}"

    def __str__(self):
        return f"{self.signature()} {{ builtin }}" if self.builtin else f"{self.signature()} {{ ... }}"
