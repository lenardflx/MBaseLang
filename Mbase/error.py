from Mbase import config

def print_error(message: str, prefix: str = "[Error]"):
    cfg = config.get_config()
    if cfg.color_support:
        print(f"\033[91m{prefix}: {message}\033[0m")  # Red
    else:
        print(f"{prefix}: {message}")

def print_error_with_origin(source: str, position: int, message: str, filename: str = "<input>", label: str = "Runtime Error"):
    cfg = config.get_config()
    lines = source.splitlines()
    char_count = 0

    for i, line in enumerate(lines):
        line_start = char_count
        line_end = char_count + len(line)
        if line_end >= position:
            col = position - char_count
            line_no = i + 1
            print(f"{filename}:{line_no}:{col + 1}")

            if cfg.color_support:
                print(f"\033[93m{line}\033[0m")
                print(f"\033[93m{' ' * col}^\033[0m")
            else:
                print(line)
                print(" " * col + "^")

            print_error(message, f"[{label}]")
            return
        char_count += len(line) + 1

    print_error(message, f"[{label}]")

