# Application Settings

APP_NAME = "Python RPG"
VERSION = "V1.1.5"
VERSION_NAME = "Bug Fixes and Settings GUI"
DEBUG_MODE = False

class UserInterfaceSettings:
    THEME = "dark"
    FONT_SIZE = 14
    SHOW_TOOLTIPS = True

class GraphicalSettings:
    RESOLUTION = [600, 800]
    FULLSCREEN = False

class GameplaySettings:
    # Affects overall game difficulty and progression, most notably enemy strength and xp gain
    GLOBAL_DIFFICULTY = 3  # 1: V. Easy, 2: Easy, 3: Normal, 4: Hard, 5: V. Hard
    AUTO_SAVE = True
    SAVE_INTERVAL = 15  # in minutes
    LEVEL_REQUIREMENTS_BASE = 40  # Base XP required for level 1
    LEVEL_SCALAR = 1.2  # Exponential scaling factor for level XP requirements

class PlayerSettings:
    STARTING_GOLD = 0
    INVENTORY_CAPACITY = 20  # Maximum number of items in inventory
    PLAYER_NAME = "Hero"
