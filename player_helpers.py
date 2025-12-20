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

    # Return the slot name as a truthy success value (UI layers may display messages)
    return slot


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
        return True
    else:
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


# --- Item comparison / auto-equip helpers ----------------------------

def get_item_slot(item):
    """Return the equipment slot that this item would occupy."""
    eff = getattr(item, 'effect', {}) or {}
    if 'attack_power' in eff:
        return 'weapon'
    elif 'armor' in eff:
        return 'armor'
    else:
        return 'accessory'


def get_item_score(item):
    """Return a heuristic numeric score for equipment comparison.

    We weight attack_power and armor higher, and include other numeric effects.
    """
    eff = getattr(item, 'effect', {}) or {}
    score = 0.0
    score += eff.get('attack_power', 0) * 2.0
    score += eff.get('armor', 0) * 1.5
    for k, v in eff.items():
        if k not in ('attack_power', 'armor'):
            try:
                score += float(v)
            except Exception:
                pass
    rarity_bonus = {'common': 0.0, 'uncommon': 1.0, 'rare': 2.0, 'epic': 3.0, 'legendary': 5.0}
    score += rarity_bonus.get(getattr(item, 'rarity', 'common'), 0.0) * 0.5
    return score


def is_better(item, current):
    """Return True if `item` is strictly better than `current` based on score."""
    if current is None:
        return True
    try:
        return get_item_score(item) > get_item_score(current)
    except Exception:
        return False


def add_loot(items):
    """Try to add loot items to player's inventory; report if inventory full.

    If an equipment item is acquired and it is better than the currently equipped
    item for that slot, auto-equip it (best-effort)."""
    for it in items:
        if len(player.get('inventory', [])) < player.get('inventory_capacity', 10):
            player['inventory'].append(it)
            TextFuncs.var_speed_print(f"Acquired {it.name}.", 0.02, 0.04)

            # Auto-equip equipment if it's better than the current
            if getattr(it, 'item_type', None) == 'equipment':
                slot = get_item_slot(it)
                current = player['equipment'].get(slot)
                try:
                    if is_better(it, current):
                        equip_item(it)
                        TextFuncs.var_speed_print(f"Auto-equipped {it.name} (better than current {current.name if current else 'None'}).", 0.02, 0.04)
                        try:
                            from main import update_equipment_panel
                            update_equipment_panel()
                        except Exception:
                            pass
                except Exception:
                    pass
        else:
            TextFuncs.var_speed_print(f"No inventory space for {it.name}.", 0.02, 0.04)