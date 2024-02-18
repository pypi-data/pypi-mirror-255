from colorama import Fore, Style
from datetime import datetime
from colorsys import hsv_to_rgb
from typing   import Dict
from shutil   import get_terminal_size

from .console import Settings


class BetaConsole:
    def __init__(self, speed: int = 2, showMS: int = 4):
        self.colHue = 120
        self.speed = speed
        self.direction = self.speed
        self.showMS = showMS
        self.extraSpace = 0
        self.incrementing = True

    def getTimestamp(self, type: int = 1) -> str:
        """
        Verilen türe göre renkli gösterime sahip bir zaman damgası alın.

        Args:
            type (int): Renk türü. Varsayılan değer 1 (RAINBOW).

        Returns:
            str: Renkli zaman damgası dizesi.

        Raises:
            ValueError:Tür geçerli aralıkta değilse (1-4).
            
        Types:
            1: "RAINBOW"\n
            2: "GREEN_TO_BLUE"\n
            3: "RED_TO_YELLOW"\n
            4: "BLUE_TO_PURPLE"\n
        """

        types: Dict[int, str] = {
            1: "RAINBOW",
            2: "GREEN_TO_BLUE",
            3: "RED_TO_YELLOW",
            4: "BLUE_TO_PURPLE"
        }
        if type not in types:
            raise ValueError("Türler aralıkta olmalıdır (1,4).")

        if type == 1:  # RAINBOW
            first_Color = 360
            second_Color = 0
        elif type == 2:  # GREEN_TO_BLUE
            first_Color = 240
            second_Color = 120
        elif type == 3:  # RED_TO_YELLOW
            first_Color = 60
            second_Color = 0
        elif type == 4:  # BLUE_TO_PURPLE
            first_Color = 300
            second_Color = 240
        
        rgb = hsv_to_rgb(self.colHue / 360, 1, 1)
        red = int(rgb[0] * 255)
        green = int(rgb[1] * 255)
        blue = int(rgb[2] * 255)

        current_time = datetime.now().strftime("%H:%M:%S.%f")[:-self.showMS]
        timestamp = f"\033[38;2;{red};{green};{blue}m{current_time}\033[0m"

        self.colHue += self.direction
        if self.colHue >= first_Color:
            self.direction = -self.speed
        elif self.colHue <= second_Color:
            self.direction = self.speed

        return timestamp

    def alphaPrint(self, type, text, increment:bool=False):
        if increment:
            if self.extraSpace == 0: self.incrementing = True
            elif self.extraSpace == 10: self.incrementing = False
            if self.incrementing: self.extraSpace += 1
            else: self.extraSpace -= 1

        console_width = get_terminal_size().columns

        other_len = 28 # avg of # len(text.split("\x1b[0m] ")[0])
        text_length = len(text.split("\x1b[0m] ")[1]) # renkler yüzünden değişip duruyor
        type_length = len(type)
        
        spaces = max(0, console_width - (text_length - type_length + other_len + self.extraSpace))
        
        if "err" in type.lower():
            form_color = Fore.RED
        elif "inf" in type.lower():
            form_color = Fore.LIGHTCYAN_EX
        else:
            form_color = Fore.GREEN
        formatted_info = type.replace("[", f"{Settings.c_SECO}[{form_color}").replace("]", f"{Settings.c_SECO}]{Style.RESET_ALL}")


        output = f"{text}{' ' * spaces}{formatted_info}"

        print(output)
        return