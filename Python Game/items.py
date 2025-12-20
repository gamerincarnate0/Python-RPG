# Item class definition

class Item:
    def __init__(self, name, item_type, effect, value, rarity='common'):
        self.name = name
        self.item_type = item_type  # eg, "consumable", "equipment"
        self.effect = effect        # eg, {"health": +50}
        self.value = value          # eg, gold value
        # Rarity: common, uncommon, rare, epic, legendary
        self.rarity = rarity

    def description(self):
        """Return a multi-line description of the item for tooltips and UI."""
        parts = [f"Name: {self.name}", f"Type: {self.item_type}", f"Rarity: {self.rarity}", f"Value: {self.value} gold"]
        if self.effect:
            eff_lines = [f"  {k}: {v}" for k, v in self.effect.items()]
            parts.append("Effects:")
            parts.extend(eff_lines)
        return "\n".join(parts)

    def _is_mapping(self, target):
        return isinstance(target, dict)

    def _has_stat(self, target, stat):
        if self._is_mapping(target):
            return stat in target
        return hasattr(target, stat)

    def _get_stat(self, target, stat):
        if self._is_mapping(target):
            return target.get(stat)
        return getattr(target, stat)

    def _set_stat(self, target, stat, value):
        if self._is_mapping(target):
            target[stat] = value
        else:
            setattr(target, stat, value)

    def check_overflow(self, target, stat, change):
        if stat in ["health", "mana"]:
            max_stat = f"max_{stat}"
            if self._has_stat(target, max_stat):
                current = self._get_stat(target, stat) or 0
                max_val = self._get_stat(target, max_stat) or 0
                if current + change > max_val:
                    return max_val - current
        return change

    def use(self, target):
        for stat, change in self.effect.items():
            if self._has_stat(target, stat):
                current = self._get_stat(target, stat) or 0
                delta = self.check_overflow(target, stat, change)
                self._set_stat(target, stat, current + delta)

        # remove this item from the passed target's inventory if present
        try:
            if self._is_mapping(target) and "inventory" in target:
                target["inventory"].remove(self)
            elif hasattr(target, "inventory"):
                inv = getattr(target, "inventory")
                if hasattr(inv, "remove"):
                    inv.remove(self)
        except ValueError:
            # ignore if not in inventory
            pass

# Potion definitions
health_potion = Item("Health Potion", "consumable", {"health": 40}, 10, rarity='common')
mana_potion = Item("Mana Potion", "consumable", {"mana": 10}, 8, rarity='common')
strength_elixir = Item("Strength Elixir", "consumable", {"strength": 5}, 15, rarity='uncommon')
agility_elixir = Item("Agility Elixir", "consumable", {"agility": 5}, 15, rarity='uncommon')
intelligence_elixir = Item("Intelligence Elixir", "consumable", {"intelligence": 5}, 15, rarity='uncommon')

# Weapon definitions
iron_sword = Item("Iron Sword", "equipment", {"attack_power": 10}, 50, rarity='uncommon')
steel_axe = Item("Steel Axe", "equipment", {"attack_power": 15}, 75, rarity='rare')
magic_staff = Item("Magic Staff", "equipment", {"attack_power": 12, "intelligence": 3}, 100, rarity='rare')

# Armor definitions
leather_armor = Item("Leather Armor", "equipment", {"armor": 5}, 40, rarity='uncommon')
chainmail_armor = Item("Chainmail Armor", "equipment", {"armor": 10}, 80, rarity='rare')
plate_armor = Item("Plate Armor", "equipment", {"armor": 15}, 120, rarity='epic')

# Jewelry definitions
silver_ring = Item("Silver Ring", "equipment", {"mana": 10}, 30, rarity='uncommon')
gold_necklace = Item("Gold Necklace", "equipment", {"health": 20}, 60, rarity='rare')


# Registry helpers for serialization/deserialization
ITEM_REGISTRY = {
    health_potion.name: health_potion,
    mana_potion.name: mana_potion,
    strength_elixir.name: strength_elixir,
    agility_elixir.name: agility_elixir,
    intelligence_elixir.name: intelligence_elixir,
    iron_sword.name: iron_sword,
    steel_axe.name: steel_axe,
    magic_staff.name: magic_staff,
    leather_armor.name: leather_armor,
    chainmail_armor.name: chainmail_armor,
    plate_armor.name: plate_armor,
    silver_ring.name: silver_ring,
    gold_necklace.name: gold_necklace,
}


def get_item_by_name(name):
    """Return an Item instance by name from registry, or None if not found."""
    return ITEM_REGISTRY.get(name)
