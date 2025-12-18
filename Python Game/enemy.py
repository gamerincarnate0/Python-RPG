# Enemy class definition

from functions import TextFuncs

class Enemy:
    def __init__(self, name, health, attack_power, armor, tier):
        self.name = name
        self.health = health
        self.attack_power = attack_power
        self.armor = armor
        self.tier = tier

    def attack(self):
        return self.attack_power

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0
    
enemy_names = {
    "tier1": ["Goblin", "Skeleton", "Zombie", "Bandit", "Wolf", "Slime", "Bat", "Spider", "Rat", "Kobold"],
    "tier2": ["Orc", "Troll", "Dark Knight", "Imp", "Ghoul", "Mimic", "Giant Ant", "Cave Bear", "Fledgeling Lich", "Harpy", "Demon"],
    "tier3": ["Minotaur", "Hydra", "Vampire", "Wraith", "Gorgon", "Cyclops", "Fire Elemental", "Ice Golem", "Shadow Beast", "Lich", "Demon Noble"],
    "tier4": ["Dragon", "Demon Prince", "Ancient Lich"],
    "tier5": ["Elder Dragon", "Demon King"]
}

enemy_stats = {
    "tier1": {"health": 50, "attack_power": 5, "armor": 2},
    "tier2": {"health": 150, "attack_power": 15, "armor": 5},
    "tier3": {"health": 300, "attack_power": 30, "armor": 10},
    "tier4": {"health": 600, "attack_power": 60, "armor": 20},
    "tier5": {"health": 1200, "attack_power": 120, "armor": 40}
}

def generate_enemy(tier):
    import random
    name = random.choice(enemy_names[tier])
    stats = enemy_stats[tier]
    return Enemy(name, stats["health"], stats["attack_power"], stats["armor"], tier)

# Example usage:
# enemy = generate_enemy("tier1")
# TextFuncs.var_speed_print(f"Generated random enemy: {enemy.name} with " + TextFuncs.color_text(f"{enemy.health} HP", "red") + " and " + TextFuncs.color_text(f"{enemy.attack_power} AP", "blue"), 0.03, 0.05)