# Enemy class definition

import random
import math

from functions import TextFuncs
from plugins.registry import PluginRegistry

class Enemy:
    def __init__(self, name, health, attack_power, armor, tier, inventory=None):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack_power = attack_power
        self.armor = armor
        self.tier = tier
        # simple inventory support for potions, etc.
        self.inventory = inventory or []

    def attack(self):
        return self.attack_power

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self):
        return self.health > 0

    def decide_action(self, player):
        """Decide the enemy's next action based on current HP and available items.

        Returns one of: 'attack', 'defend', 'heal'.
        """
        import random
        hp_pct = (self.health / self.max_health) if self.max_health else 0

        # If very low on HP prefer to heal (if potion present) or defend
        has_potion = any(getattr(it, 'name', None) == 'Health Potion' for it in self.inventory)
        if hp_pct < 0.30:
            if has_potion and random.random() < 0.75:
                return 'heal'
            if random.random() < 0.6:
                return 'defend'
            return 'attack'

        # If moderately hurt, sometimes defend
        if hp_pct < 0.6:
            if random.random() < 0.35:
                return 'defend'
            return 'attack'

        # otherwise attack
        return 'attack'
    
def get_enemy_templates_for_tier(tier: str, registry: PluginRegistry):
    """Return all enemy templates (plugin + vanilla) for a tier."""
    plugin_templates = registry.get_enemies_for_tier(tier)

    # Fallback: build vanilla templates from your old tables
    vanilla = []
    for name in enemy_names.get(tier, []):
        vanilla.append({
            "name": name,
            "tier": tier,
            "base_stats": enemy_stats[tier]
        })

    return plugin_templates + vanilla

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

def get_difficulty_multiplier(difficulty=None):
    """Return the scaling multiplier for a given difficulty (defaults to GameplaySettings.GLOBAL_DIFFICULTY)."""
    from settings import GameplaySettings
    d = difficulty if (difficulty is not None) else GameplaySettings.GLOBAL_DIFFICULTY
    return 1.0 + (d - 3) * 0.15

def generate_enemy(tier, registry: PluginRegistry):
    import random
    from items import health_potion
    from settings import GameplaySettings

    templates = get_enemy_templates_for_tier(tier, registry)
    template = random.choice(templates)

    stats = template["base_stats"]

    multiplier = get_difficulty_multiplier()

    base_hp = stats["health"] * multiplier
    base_attack = max(1, int(stats["attack_power"] * multiplier))
    base_armor = max(0, int(stats["armor"] * multiplier))

    hp = math.ceil(random.uniform(
        base_hp * 0.9,
        base_hp * 1.1
    ))

    e = Enemy(
        template["name"],
        hp,
        base_attack,
        base_armor,
        tier
    )

    # ---- everything below this line is almost unchanged ----

    xp_table = {"tier1": 8, "tier2": 25, "tier3": 60, "tier4": 150, "tier5": 400}
    gold_table = {"tier1": (5, 15), "tier2": (20, 50), "tier3": (50, 120), "tier4": (150, 400), "tier5": (500, 1500)}

    base_xp = xp_table.get(tier, 10)
    e.xp_reward = max(1, int(base_xp * multiplier))

    gmin, gmax = gold_table.get(tier, (5, 10))
    gmin = max(1, int(gmin * multiplier))
    gmax = max(gmin, int(gmax * multiplier))
    e.gold_reward = random.randint(gmin, gmax)

    e.loot = []

    if random.random() < 0.25:
        e.inventory.append(health_potion)

    return e


def generate_enemy_for_player(player_level: int, registry: PluginRegistry):
    if player_level <= 3:
        tier = 'tier1'
    elif player_level <= 7:
        tier = 'tier2'
    elif player_level <= 11:
        tier = 'tier3'
    elif player_level <= 15:
        tier = 'tier4'
    else:
        tier = 'tier5'

    e = generate_enemy(tier, registry)

    level_mult = 1.0 + max(0, (player_level - 1)) * 0.05

    e.max_health = max(1, int(e.max_health * level_mult))
    e.health = max(0, min(e.max_health, int(e.health * level_mult)))
    e.attack_power = max(1, int(e.attack_power * level_mult))
    e.armor = max(0, int(e.armor * level_mult))

    e.xp_reward = max(1, int(e.xp_reward * (1.0 + (player_level - 1) * 0.02)))
    e.gold_reward = max(0, int(e.gold_reward * (1.0 + (player_level - 1) * 0.02)))

    return e