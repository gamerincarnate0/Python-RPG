import time
import random
from colorama import init, Fore, Style

init(autoreset=False)

class TextFuncs:
    # Optional GUI logger callback that can be set by the UI (main window).
    # The callback signature is: func(text, rarity=None)
    _gui_logger = None

    @staticmethod
    def set_gui_logger(func):
        TextFuncs._gui_logger = func

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
        # If a GUI logger has been registered, send the text there immediately
        try:
            if TextFuncs._gui_logger:
                try:
                    TextFuncs._gui_logger(text)
                    return
                except Exception:
                    # If GUI logger fails, fallback to terminal printing
                    pass
        except Exception:
            pass

        # Fallback: character-by-character terminal print
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay + random.uniform(0, offset))
        print()  # For newline after the text is printed


# --- Save / Load Game --------------------------------------------------
import json
import os
from items import get_item_by_name


def _serialize_player():
    """Create a JSON-serializable dict for the current player state."""
    from player import player
    data = {}
    # Primitive fields
    fields = ['name', 'level', 'experience', 'health', 'max_health', 'strength', 'agility', 'gold', 'inventory_capacity', 'attack_power_bonus', 'armor_bonus']
    for f in fields:
        data[f] = player.get(f)
    # Inventory as names
    data['inventory'] = [getattr(it, 'name', None) for it in player.get('inventory', [])]
    # Equipment as names or None
    data['equipment'] = {slot: (getattr(it, 'name', None) if it else None) for slot, it in player.get('equipment', {}).items()}
    return data


def _deserialize_player(d):
    """Load player dict values from deserialized JSON content `d`."""
    from player import player
    # Primitive fields (only set if present)
    fields = ['name', 'level', 'experience', 'health', 'max_health', 'strength', 'agility', 'gold', 'inventory_capacity', 'attack_power_bonus', 'armor_bonus']
    for f in fields:
        if f in d:
            player[f] = d[f]
    # Inventory
    player['inventory'] = []
    for name in d.get('inventory', []):
        it = get_item_by_name(name)
        if it:
            player['inventory'].append(it)
    # Equipment
    eq = d.get('equipment', {}) or {}
    for slot in ('weapon', 'armor', 'accessory'):
        nm = eq.get(slot)
        player['equipment'][slot] = get_item_by_name(nm) if nm else None


def save_game(filepath='savegame.json'):
    """Write the current player state to `filepath` (JSON). Returns True on success."""
    try:
        data = {'player': _serialize_player()}
        with open(filepath, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, indent=2)
        return True
    except Exception:
        return False


def load_game(filepath='savegame.json'):
    """Load player state from `filepath` (JSON). Returns True on success."""
    if not os.path.exists(filepath):
        return False
    try:
        with open(filepath, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        _deserialize_player(data.get('player', {}))
        return True
    except Exception:
        return False