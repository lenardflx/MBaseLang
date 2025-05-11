from Mbase import config, execute
import sys

def main():
    config.init()

    if len(sys.argv) > 1:
        execute.run_file(sys.argv[1])
    else:
        execute.repl()
