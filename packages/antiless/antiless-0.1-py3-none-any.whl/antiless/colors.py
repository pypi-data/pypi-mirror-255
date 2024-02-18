from colorama import Fore as C
from enum     import Enum, auto

class Color(Enum):
    RESET           = C.RESET

    BLACK           = C.BLACK
    RED             = C.RED
    GREEN           = C.GREEN
    YELLOW          = C.YELLOW
    BLUE            = C.BLUE
    MAGENTA         = C.MAGENTA
    CYAN            = C.CYAN
    WHITE           = C.WHITE

    LIGHTBLACK      = C.LIGHTBLACK_EX
    LIGHTRED        = C.LIGHTRED_EX
    LIGHTGREEN      = C.LIGHTGREEN_EX
    LIGHTYELLOW     = C.LIGHTYELLOW_EX
    LIGHTBLUE       = C.LIGHTBLUE_EX
    LIGHTMAGENTA    = C.LIGHTMAGENTA_EX
    LIGHTCYAN       = C.LIGHTCYAN_EX
    LIGHTWHITE      = C.LIGHTWHITE_EX

    CUSTOM1 = "\x1b[38;5;213m"
    CUSTOM2 = "\x1b[38;5;253m"
    CUSTOM3 = "\x1b[48;5;161m"