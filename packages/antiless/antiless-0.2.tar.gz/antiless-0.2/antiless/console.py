from colorama    import Fore
from datetime    import datetime
from time        import time
from re          import sub
from dataclasses import dataclass
from typing      import Literal


@dataclass
class Settings:
    initialized: bool = False
    debug:       bool = True 
    timestamp:   bool = True
    wrapTime:    bool = False
    c_MAIN:    str = Fore.LIGHTBLUE_EX
    c_SECO:    str = Fore.LIGHTBLACK_EX
    LOGPRESET: str = "default"
    presets = {
        "default": {
            "Primary":   Fore.RESET,
            "Secondary": c_SECO,
            
            "TSFormat":  "%H:%M:%S",
            
            "SucMsg":    f"{Fore.GREEN}YES",
            "InfMsg":    f"{Fore.LIGHTMAGENTA_EX}INF",
            "DbgMsg":    f"{Fore.LIGHTYELLOW_EX}DBG",
            "ErrorMsg":  f"{Fore.LIGHTRED_EX}ERR",
            "FtlMsg":    f"{Fore.RED}FTL",
            
            "ShowBracket": False
        },
        "preset_1": {
            "Primary":   "\x1b[38;5;213m",
            "Secondary": "\x1b[38;5;253m",
            
            "TSFormat":  "%H:%M",
            
            "SucMsg":    "\x1b[48;5;165m ✓ \x1b[0m",
            "InfMsg":    "\x1b[38;5;213m\x1b[1mINF\x1b[0m",
            "DbgMsg":    f"{Fore.LIGHTMAGENTA_EX}DBG",
            "ErrorMsg":  "\x1b[48;5;161m ! \x1b[0m",
            "FtlMsg":    f"{Fore.RED}FTL",
            
            "ShowBracket": True
        }
    }


def init(
    debug: bool = True,
    showTimestamp: bool = True,
    wrapTime: bool = True,
    colMain = Fore.LIGHTBLUE_EX,
    colSeco = Fore.LIGHTBLACK_EX,
    logpreset: Literal["default", "preset_1", "custom_preset"] = "default",
    custom_preset: dict = None
):
    Settings.initialized = True
    Settings.debug = debug
    Settings.timestamp = showTimestamp
    Settings.c_MAIN = colMain
    Settings.c_SECO = colSeco
    Settings.wrapTime = wrapTime
    Settings.LOGPRESET = logpreset
    if custom_preset: Settings.presets["custom_preset"] = custom_preset
    

@staticmethod
def printf(content: str, mainCol = None, showTimestamp = None):
    """
    Contenti isteğe bağlı renkli metin ve zaman damgası ile yazdırın.

    Args:
        content (str): Yazdırılacak content.
        mainCol (str, optional): Ön ekin ana rengi. Varsayılan değer Settings.mainColOR (LIGHTBLUE)'dur.
        showTimestamp (bool, optional): Zaman damgasının gösterilip gösterilmeyeceği. Varsayılan değer True'dur (show timestamp).
    """
    if showTimestamp is None:
        showTimestamp = Settings.timestamp
    if mainCol is None:
        mainCol = Settings.c_MAIN

    if not isinstance(content, str):
        return print(content)

    debug_markers = ["(!)", "(-)", "(~)", "debug"]
    if any(marker in content for marker in debug_markers) and not Settings.debug:
        return

    timestamp = ""
    if showTimestamp:
        timestamp = f"[{Settings.c_SECO}{datetime.fromtimestamp(time()).strftime('%H:%M:%S')}{Fore.RESET}]"
        if not Settings.wrapTime:
            timestamp = timestamp[1:-1]
            
    content   = sub(r'\[(.*?)]', rf'{Settings.c_SECO}[{mainCol}\1{Settings.c_SECO}]{Fore.RESET}', content)
    replacements = {
        "|": f"{Settings.c_SECO}|{mainCol}",
        "->": f"{Settings.c_SECO}->{mainCol}",
        "(+)": f"{Settings.c_SECO}({Fore.GREEN}+{Settings.c_SECO}){mainCol}",
        "($)": f"{Settings.c_SECO}({Fore.GREEN}${Settings.c_SECO}){mainCol}",
        "(-)": f"{Settings.c_SECO}({Fore.RED}-{Settings.c_SECO}){mainCol}",
        "(!)": f"{Settings.c_SECO}({Fore.RED}!{Settings.c_SECO}){mainCol}",
        "(~)": f"{Settings.c_SECO}({Fore.YELLOW}~{Settings.c_SECO}){mainCol}",
        "(#)": f"{Settings.c_SECO}({Fore.BLUE}#{Settings.c_SECO}){mainCol}",
        "(*)": f"{Settings.c_SECO}({Fore.CYAN}*{Settings.c_SECO}){mainCol}",
    }

    for find, replace in replacements.items():
        content = content.replace(find, replace)

    print(timestamp, content, end=f"{Fore.RESET}\n")
    
        
    
@staticmethod
def inputf(content: str):
    if "(?)" not in content: x = f"{Settings.c_SECO}({Settings.c_MAIN}?{Settings.c_SECO}){Fore.RESET} "
    else: x = ""
    content = x + content\
        .replace("(", f"{Settings.c_SECO}({Settings.c_MAIN}").replace(")", f"{Settings.c_SECO}){Settings.c_MAIN}")\
        .replace(">", f"{Settings.c_SECO}>{Fore.RESET}")
    return input(content)