# Player definition

from settings import PlayerSettings, GameplaySettings
from functions import TextFuncs

player = {
    "name": PlayerSettings.PLAYER_NAME,
    "level": 1,
    "health": 40,
    "max_health": 100,
    "mana": 50,
    "max_mana": 50,
    "strength": 10,
    "agility": 10,
    "intelligence": 10,
    "experience": 0,
    "gold": PlayerSettings.STARTING_GOLD,
    "inventory": [],
    "inventory_capacity": PlayerSettings.INVENTORY_CAPACITY,
    "skills": [],
    "effects": []
}

@staticmethod
def calculate_experience_to_next_level(level):
    base_xp = GameplaySettings.LEVEL_REQUIREMENTS_BASE
    scalar = GameplaySettings.LEVEL_SCALAR
    return int(base_xp * (scalar ** (level - 1)))

@staticmethod
def display_player_stats():
    stats = (
        f"Name: {player['name']}\n"
        f"Level: {player['level']}\n"
        f"Experience: {TextFuncs.color_text(f'{player['experience']}/{calculate_experience_to_next_level(player['level'])}', 'cyan')}\n"
        f"Health: {TextFuncs.color_text(f'{player['health']}/{player['max_health']}', 'red')}\n"
        f"Mana: {TextFuncs.color_text(f'{player['mana']}/{player['max_mana']}', 'green')}\n"
        f"Strength: {player['strength']}\n"
        f"Agility: {player['agility']}\n"
        f"Intelligence: {player['intelligence']}\n"
        f"Gold: {TextFuncs.color_text(f'{player['gold']}', 'yellow')}\n"
        f"Inventory Slots Used: {len(player['inventory'])}/{player['inventory_capacity']}\n"
        f"Items: {[item.name for item in player['inventory']]}\n"
        f"Skills: {[skill.name for skill in player['skills']]}\n"
        f"Active Effects: {[effect.name for effect in player['effects']]}\n"
    )
    TextFuncs.var_speed_print(stats, 0.03, 0.05)

@staticmethod
def display_only_inventory():
    TextFuncs.var_speed_print(f"Items: {[item.name for item in player['inventory']]}\n", 0.03, 0.05)