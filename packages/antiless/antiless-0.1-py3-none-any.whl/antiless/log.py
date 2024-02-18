from datetime import datetime
from time import time
from colorama import Fore, init as colinit
from .colors import *
from .console import Settings
from re import sub


class log:
    def __init__(self) -> None:
        colinit(autoreset=True)

    @staticmethod
    def _get_timestamp():
        settings = Settings.presets.get(Settings.LOGPRESET, Settings.presets["default"])
        if Settings.timestamp:
            timestamp = (
                f"{settings.get('Primary')}[" if settings.get("ShowBracket") else ""
            ) + (
                f"{settings.get('Secondary')}"
                + f"{datetime.fromtimestamp(time()).strftime(settings.get('TSFormat'))}"
            ) + (
                f"{settings.get('Primary')}]" if settings.get("ShowBracket") else ""
            ) + f"{Fore.RESET}"
        else:
            timestamp = ""
        return timestamp, settings

    @staticmethod
    def _log_message(level, text, sep=" "):
        timestamp, settings = log._get_timestamp()
        xcol = settings.get("Primary")
        try: text = sub(r'\[(.*?)]', rf'{Settings.c_SECO}[{xcol}\1{Settings.c_SECO}]{Fore.RESET}', text)
        except: pass
        print(
            f"{timestamp} {settings.get(level)} {Fore.LIGHTBLACK_EX}{sep}{Fore.RESET}{text}"
        )

    @staticmethod
    def success(text: str, sep: str = " "):
        log._log_message("SucMsg", text, sep)

    @staticmethod
    def debug(text: str, sep: str = " "):
        log._log_message("DbgMsg", text, sep)

    @staticmethod
    def info(text: str, sep: str = " "):
        log._log_message("InfMsg", text, sep)

    @staticmethod
    def error(text: str, sep: str = " "):
        log._log_message("ErrorMsg", text, sep)

    @staticmethod
    def fatal(text: str, sep: str = " "):
        log._log_message("FtlMsg", text, sep)

    @staticmethod
    def log(text, **kwargs):
        gray = "\033[90m"  # Gri renk için ANSI escape kodu
        reset = "\033[0m"  # Rengi sıfırlamak için ANSI escape kodu

        log_message = f"{text} " + " ".join([f"{gray}{key}={reset}{value}" for key, value in kwargs.items()])
        print(log._get_timestamp()[0], log_message)

    @staticmethod
    def vert(text, **kwargs):
        gray = "\033[90m"
        reset = "\033[0m"

        ts, settings = log._get_timestamp()
        maincol = settings.get("InfMsg")
        mcol = settings.get("Primary")
        
        log_message = f"{maincol} {text}"
        
        first_len = len(log_message)
        for index, (key, value) in enumerate(kwargs.items()):
            prefix = "\t ├" if index < len(kwargs) - 1 else "\t └"
            line = f"{prefix} {mcol}{key}:{Fore.RESET} {value}"
            line = line.rjust(first_len-len(text)-5)
            log_message += f"\n{line}"
            
        print(ts, log_message)