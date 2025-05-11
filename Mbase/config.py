import datetime
import os
import sys
import time

class Config:
    def __init__(self):
        self.app_name = "MBase"
        self.version = "0.1.0"
        self.author = "MBase Team"
        self.description = "A simple programming language for educational purposes."
        self.license = "MIT"

        # REPL settings
        self.repl_prompt = "MBase> "
        self.repl_multiline_prompt = "... > "

        # File settings
        self.file_encoding = "utf-8"
        self.file_extension = ".mbl"

        # Startup time
        self.start_time = time.time()
        self.color_support = self._detect_color_support()

    @staticmethod
    def _detect_color_support():
        return sys.stdout.isatty() and (
            os.environ.get("TERM") != "dumb" or os.name == "nt"
        )

    def display_startup(self):
        timestamp = datetime.datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{self.app_name} {self.version} - {timestamp}")
        print("Type 'exit' to exit.")


_config_instance: Config | None = None

def init() -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

def get_config() -> Config:
    if _config_instance is None:
        raise RuntimeError("Config not initialized. Call init() first.")
    return _config_instance
