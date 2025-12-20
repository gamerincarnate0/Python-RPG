# Enemy class definition

import random
import math

from functions import TextFuncs

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


def generate_enemy(tier):
    import random
    from items import health_potion, iron_sword, leather_armor, plate_armor, steel_axe
    from settings import GameplaySettings

    name = random.choice(enemy_names[tier])
    stats = enemy_stats[tier]

    multiplier = get_difficulty_multiplier()

    base_hp = stats["health"] * multiplier
    base_attack = max(1, int(stats["attack_power"] * multiplier))
    base_armor = max(0, int(stats["armor"] * multiplier))

    hp = math.ceil(random.uniform(base_hp - (base_hp * 0.1), base_hp + (base_hp * 0.1)))
    e = Enemy(name, hp, base_attack, base_armor, tier)

    # Reward scaling by tier and difficulty
    xp_table = {"tier1": 8, "tier2": 25, "tier3": 60, "tier4": 150, "tier5": 400}
    gold_table = {"tier1": (5, 15), "tier2": (20, 50), "tier3": (50, 120), "tier4": (150, 400), "tier5": (500, 1500)}

    base_xp = xp_table.get(tier, 10)
    e.xp_reward = max(1, int(base_xp * multiplier))

    gmin, gmax = gold_table.get(tier, (5, 10))
    gmin = max(1, int(gmin * multiplier))
    gmax = max(gmin, int(gmax * multiplier))
    e.gold_reward = random.randint(gmin, gmax)

    # Ensure loot container exists
    e.loot = []

    # 25% chance to carry a health potion so some enemies can heal
    if random.random() < 0.25:
        e.inventory.append(health_potion)

    # Expanded loot table with more items and better variety
    from items import mana_potion, strength_elixir, agility_elixir, intelligence_elixir, magic_staff, chainmail_armor, silver_ring, gold_necklace
    LOOT_TABLE = {
        "tier1": [
            (health_potion, 60), (mana_potion, 20), (leather_armor, 10), (iron_sword, 5), (strength_elixir, 5)
        ],
        "tier2": [
            (health_potion, 40), (mana_potion, 20), (leather_armor, 10), (iron_sword, 10), (steel_axe, 7), (strength_elixir, 6), (agility_elixir, 5), (silver_ring, 2)
        ],
        "tier3": [
            (health_potion, 25), (mana_potion, 15), (leather_armor, 8), (chainmail_armor, 10), (iron_sword, 8), (steel_axe, 10), (plate_armor, 5), (strength_elixir, 6), (agility_elixir, 5), (intelligence_elixir, 5), (magic_staff, 4), (silver_ring, 3), (gold_necklace, 2)
        ],
        "tier4": [
            (health_potion, 15), (mana_potion, 10), (chainmail_armor, 10), (plate_armor, 10), (iron_sword, 6), (steel_axe, 8), (magic_staff, 7), (strength_elixir, 5), (agility_elixir, 5), (intelligence_elixir, 5), (silver_ring, 4), (gold_necklace, 4)
        ],
        "tier5": [
            (health_potion, 10), (mana_potion, 8), (chainmail_armor, 8), (plate_armor, 15), (iron_sword, 5), (steel_axe, 7), (magic_staff, 10), (strength_elixir, 5), (agility_elixir, 5), (intelligence_elixir, 5), (silver_ring, 5), (gold_necklace, 6)
        ],
    }

    # chance to drop an item increases with difficulty
    drop_chance = 0.2 * multiplier
    if random.random() < drop_chance:
        choices, weights = zip(*LOOT_TABLE.get(tier, LOOT_TABLE["tier1"]))
        chosen = random.choices(choices, weights=weights, k=1)[0]
        e.loot.append(chosen)

    return e


def generate_enemy_for_player(player_level: int):
    """Generate an enemy scaled to the player's level.

    The function picks a tier based on ranges of player levels and applies an
    additional scaling multiplier to HP/attack/armor based on level so fights
    remain challenging as players progress.
    """
    # Tier mapping: levels 1-3 -> tier1, 4-7 -> tier2, 8-11 -> tier3, 12-15 -> tier4, 16+ -> tier5
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

    e = generate_enemy(tier)

    # Apply a gentle per-level scaling (5% per level beyond level 1)
    level_mult = 1.0 + max(0, (player_level - 1)) * 0.05

    # Scale max_health, current health, attack_power, and armor
    e.max_health = max(1, int(e.max_health * level_mult))
    e.health = max(0, min(e.max_health, int(e.health * level_mult)))
    e.attack_power = max(1, int(e.attack_power * level_mult))
    e.armor = max(0, int(e.armor * level_mult))

    # Optionally scale rewards slightly with level
    e.xp_reward = max(1, int(e.xp_reward * (1.0 + (player_level - 1) * 0.02)))
    e.gold_reward = max(0, int(e.gold_reward * (1.0 + (player_level - 1) * 0.02)))

    return e