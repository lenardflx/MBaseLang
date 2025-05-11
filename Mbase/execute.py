from Interpreter.evaluate import evaluate
from Mbase import config
from Mbase.error import print_error_with_origin, print_error
from Parser import tokenizer
from Parser.parse import Parser
from Mbase.builtin import *

def repl():
    cfg = config.get_config()
    cfg.display_startup()

    open_braces = 0
    buffer = ""
    ctx = {}

    while True:
        try:
            prompt = cfg.repl_multiline_prompt if open_braces > 0 else cfg.repl_prompt
            user_input = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.strip().lower() in ["exit", "quit"]:
            break
        if not user_input and not buffer:
            continue

        open_braces += user_input.count("{") - user_input.count("}")
        buffer += user_input + "\n"
        if open_braces > 0:
            continue

        _run_buffer(buffer, ctx)
        buffer = ""
        open_braces = 0


def run_file(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        print_error(str(e), f"[File Error]: Cannot open file '{path}'")
        return

    ctx = {}
    _run_buffer(source, ctx, filename=path)


def _run_buffer(source: str, ctx: dict, filename: str = "<input>"):
    is_repl = filename == "<input>"
    ctx["__source__"] = source
    ctx["__filename__"] = filename
    ctx["__origin__"] = "<repl>" if is_repl else filename
    ctx["__functions__"] = BUILTINS

    try:
        tokens = list(tokenizer.tokenize(source))
        if not tokens:
            return
        parser = Parser(tokens)
        ast = parser.parse()
    except (SyntaxError, TypeError) as e:
        print_error(str(e), "[Syntax Error]" if isinstance(e, SyntaxError) else "[Type Error]")
        return
    except Exception as e:
        print_error(str(e), "[Parse Error]")
        return

    for expr in ast:
        try:
            result = evaluate(expr, ctx)

            if is_repl:
                if isinstance(expr, tuple) and expr[0] == "call" and expr[1] == "out":
                    print()
                if result is not None:
                    print(result)

        except Exception as e:
            pos = expr[4] if isinstance(expr, tuple) and len(expr) > 4 else None
            print_error_with_origin(source, pos, str(e), ctx["__origin__"]) if pos else print_error(str(e), "[Runtime Error]")
            return