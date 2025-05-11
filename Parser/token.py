class Token:
    def __init__(self, type_, value, pos=None):
        self.type = type_
        self.value = value
        self.pos = pos

    def __repr__(self):
        return f"Token({self.type}, {self.value})"