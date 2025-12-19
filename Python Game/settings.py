# Application Settings

APP_NAME = "Python RPG"
VERSION = "0.8.2"
VERSION_NAME = "Combat and UI Update!"
DEBUG_MODE = True

class UserInterfaceSettings:
    THEME = "dark"
    FONT_SIZE = 14
    SHOW_TOOLTIPS = True

class GraphicalSettings:
    RESOLUTION = (1920, 1080)
    FULLSCREEN = False
    VSYNC = True

class WorldSettings:
    GRAVITY = 9.81  # m/s^2
    DAY_NIGHT_CYCLE = True
    WEATHER_EFFECTS = True

class GameplaySettings:
    # Affects overall game difficulty and progression, most notably enemy strength and xp gain
    GLOBAL_DIFFICULTY = 3  # 1: V. Easy, 2: Easy, 3: Normal, 4: Hard, 5: V. Hard
    AUTO_SAVE = True
    SAVE_INTERVAL = 15  # in minutes
    MAX_LEVEL = 50 # Maximum player level, 0 for unlimited
    STAT_POINTS_PER_LEVEL = 3  # Stat points awarded per level up
    SKILL_POINTS_PER_LEVEL = 1  # Skill points awarded per level up
    LEVEL_REQUIREMENTS_BASE = 100  # Base XP required for level 1
    LEVEL_SCALAR = 1.2  # Exponential scaling factor for level XP requirements

class PlayerSettings:
    STARTING_GOLD = 0
    INVENTORY_CAPACITY = 20  # Maximum number of items in inventory, 0 for unlimited
    PLAYER_NAME = "Hero"

class AudioSettings:
    MASTER_VOLUME = 1.0  # Range: 0.0 to 1.0
    MUSIC_VOLUME = 1.0   # Range: 0.0 to 1.0
    SFX_VOLUME = 1.0     # Range: 0.0 to 1.0