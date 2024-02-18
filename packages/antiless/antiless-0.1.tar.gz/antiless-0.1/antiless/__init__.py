__title__ = 'antiless'
__author__ = '@antilag'
__version__ = '0.1'


from .console import *
from .legacy  import *
from .log     import *
from .unique  import *


from requests import get
from os import system; from sys import executable
try:
    CURRENT_VERSION = get(f"https://pypi.org/project/{__title__}/json").json().get("version")
except:
    CURRENT_VERSION = __version__
    
if __version__ < CURRENT_VERSION:
    Console.printf(
        f"[{__title__.upper()}] Sürüm Güncel Değil. Lütfen kullanarak yükseltin: \"python.exe -m pip install -U {__title__}\"", 
        mainCol=Fore.RED,
        showTimestamp=False
    )
    system(f'{executable} -m pip install -U {__title__}  -q')