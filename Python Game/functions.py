import time
import random
from colorama import init, Fore, Style

init(autoreset=False)

class TextFuncs:
    @staticmethod
    def color_text(text, color):
        colors = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "blue": Fore.BLUE,
        "yellow": Fore.YELLOW,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
        "black": Fore.BLACK,
        }
    
        # Normalize input (lowercase)
        color = color.lower()
    
        # Get color from dict, or default to white if not found
        color_code = colors.get(color, Fore.WHITE)
    
        # Return the colored text (autoreset handles reset automatically)
        return color_code + text + Style.RESET_ALL

    @staticmethod
    def var_speed_print(text, delay, offset):
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay + random.uniform(0, offset))
        print()  # For newline after the text is printed