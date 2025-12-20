# Application Settings
import configparser
import os

APP_NAME = "Python RPG"
VERSION = "V1.1.5"
VERSION_NAME = "Bug Fixes and Settings GUI"
DEBUG_MODE = False

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "settings.ini")
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

class UserInterfaceSettings:
    THEME = config.get("UserInterfaceSettings", "THEME", fallback="dark")
    FONT_SIZE = config.getint("UserInterfaceSettings", "FONT_SIZE", fallback=14)
    SHOW_TOOLTIPS = config.getboolean("UserInterfaceSettings", "SHOW_TOOLTIPS", fallback=True)

class GraphicalSettings:
    RESOLUTION = [int(x) for x in config.get("GraphicalSettings", "RESOLUTION", fallback="600,800").split(",")]
    FULLSCREEN = config.getboolean("GraphicalSettings", "FULLSCREEN", fallback=False)

class GameplaySettings:
    GLOBAL_DIFFICULTY = config.getint("GameplaySettings", "GLOBAL_DIFFICULTY", fallback=3)
    AUTO_SAVE = config.getboolean("GameplaySettings", "AUTO_SAVE", fallback=True)
    SAVE_INTERVAL = config.getint("GameplaySettings", "SAVE_INTERVAL", fallback=15)
    LEVEL_REQUIREMENTS_BASE = config.getint("GameplaySettings", "LEVEL_REQUIREMENTS_BASE", fallback=40)
    LEVEL_SCALAR = config.getfloat("GameplaySettings", "LEVEL_SCALAR", fallback=1.2)

class PlayerSettings:
    STARTING_GOLD = config.getint("PlayerSettings", "STARTING_GOLD", fallback=0)
    INVENTORY_CAPACITY = config.getint("PlayerSettings", "INVENTORY_CAPACITY", fallback=20)
    PLAYER_NAME = config.get("PlayerSettings", "PLAYER_NAME", fallback="Hero")
