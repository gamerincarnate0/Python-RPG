"""Helper functions for combat that operate on the module-level `player` dict.
Kept separate so we don't need to refactor the original `player.py` structure.
"""
import random
from functions import TextFuncs
from player import player


def is_alive():
    return player.get('health', 0) > 0


def take_damage(amount):
    player['health'] = max(0, player.get('health', 0) - amount)


def get_attack_power():
    base = player.get('strength', 10)
    bonus = player.get('attack_power_bonus', 0)
    return max(1, base // 2 + bonus + random.randint(-2, 2))


def equip_item(item):
    """Equip an equipment item. Returns True on success."""
    itype = getattr(item, 'item_type', None)
    if itype != 'equipment':
        return False

    # choose slot by effect
    slot = 'accessory'
    eff = getattr(item, 'effect', {}) or {}
    if 'attack_power' in eff:
        slot = 'weapon'
    elif 'armor' in eff:
        slot = 'armor'

    # unequip existing to inventory
    current = player['equipment'].get(slot)
    if current:
        # try to add back to inventory
        if len(player['inventory']) < player.get('inventory_capacity', 0):
            player['inventory'].append(current)
        else:
            # no space to unequip
            return False

    # remove item from inventory if present
    try:
        player['inventory'].remove(item)
    except ValueError:
        pass

    player['equipment'][slot] = item

    # apply stat bonuses
    if 'attack_power' in eff:
        player['attack_power_bonus'] = player.get('attack_power_bonus', 0) + eff['attack_power']
    if 'armor' in eff:
        player['armor_bonus'] = player.get('armor_bonus', 0) + eff['armor']

    TextFuncs.var_speed_print(f"Equipped {item.name} in slot {slot}.", 0.02, 0.04)
    return True


def unequip_item(slot):
    """Unequip item from slot and place into inventory if space; returns True if successful."""
    if slot not in player['equipment']:
        return False
    itm = player['equipment'][slot]
    if itm is None:
        return False

    eff = getattr(itm, 'effect', {}) or {}
    # remove bonuses
    if 'attack_power' in eff:
        player['attack_power_bonus'] = max(0, player.get('attack_power_bonus', 0) - eff['attack_power'])
    if 'armor' in eff:
        player['armor_bonus'] = max(0, player.get('armor_bonus', 0) - eff['armor'])

    if len(player['inventory']) < player.get('inventory_capacity', 0):
        player['inventory'].append(itm)
        player['equipment'][slot] = None
        TextFuncs.var_speed_print(f"Unequipped {itm.name} to inventory.", 0.02, 0.04)
        return True
    else:
        TextFuncs.var_speed_print("No inventory space to unequip item.", 0.02, 0.04)
        return False


def sell_item(item, sell_ratio=0.5):
    """Sell an item from inventory or equipped; returns gold gained or 0."""
    # if equipped, unequip and then sell
    for slot, itm in player['equipment'].items():
        if itm is item:
            # remove bonuses
            unequip_item(slot)
            break

    # remove from inventory
    try:
        player['inventory'].remove(item)
    except ValueError:
        return 0

    gold = int(item.value * sell_ratio)
    player['gold'] = player.get('gold', 0) + gold
    TextFuncs.var_speed_print(f"Sold {item.name} for {gold} gold.", 0.02, 0.04)
    return gold


def attack_target(target):
    dmg = get_attack_power() - getattr(target, 'armor', 0)
    dmg = max(1, dmg)
    target.take_damage(dmg)
    TextFuncs.var_speed_print(f"{player['name']} attacks {target.name} for {dmg} damage.", 0.02, 0.04)


def use_health_potion():
    for it in list(player.get('inventory', [])):
        if getattr(it, 'name', None) == 'Health Potion':
            it.use(player)
            TextFuncs.var_speed_print("You used a Health Potion.", 0.03, 0.05)
            return True
    return False


# --- XP / gold / loot helpers ------------------------------------------

def add_experience(amount):
    """Add experience and handle level-ups."""
    from player import calculate_experience_to_next_level
    player['experience'] = player.get('experience', 0) + amount
    TextFuncs.var_speed_print(f"Gained {amount} XP.", 0.02, 0.04)

    # Level up loop
    while player['experience'] >= calculate_experience_to_next_level(player['level']):
        threshold = calculate_experience_to_next_level(player['level'])
        player['experience'] -= threshold
        player['level'] += 1
        # simple stat increases
        player['max_health'] = player.get('max_health', 100) + 10
        player['strength'] = player.get('strength', 10) + 2
        player['agility'] = player.get('agility', 10) + 1
        # heal some on level up
        player['health'] = min(player['max_health'], player.get('health', 0) + player['max_health'] // 4)
        TextFuncs.var_speed_print(f"Leveled up! Now level {player['level']}", 0.02, 0.04)


def add_gold(amount):
    player['gold'] = player.get('gold', 0) + amount
    TextFuncs.var_speed_print(f"Found {amount} gold.", 0.02, 0.04)


def add_loot(items):
    """Try to add loot items to player's inventory; report if inventory full."""
    for it in items:
        if len(player.get('inventory', [])) < player.get('inventory_capacity', 10):
            player['inventory'].append(it)
            TextFuncs.var_speed_print(f"Acquired {it.name}.", 0.02, 0.04)
        else:
            TextFuncs.var_speed_print(f"No inventory space for {it.name}.", 0.02, 0.04)