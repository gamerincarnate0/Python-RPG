# Item class definition

class Item:
    def __init__(self, name, item_type, effect, value):
        self.name = name
        self.item_type = item_type  # eg, "consumable", "equipment"
        self.effect = effect        # eg, {"health": +50}
        self.value = value          # eg, gold value

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
health_potion = Item("Health Potion", "consumable", {"health": 40}, 10)
mana_potion = Item("Mana Potion", "consumable", {"mana": 10}, 8)
strength_elixir = Item("Strength Elixir", "consumable", {"strength": 5}, 15)
agility_elixir = Item("Agility Elixir", "consumable", {"agility": 5}, 15)
intelligence_elixir = Item("Intelligence Elixir", "consumable", {"intelligence": 5}, 15)

# Weapon definitions
iron_sword = Item("Iron Sword", "equipment", {"attack_power": 10}, 50)
steel_axe = Item("Steel Axe", "equipment", {"attack_power": 15}, 75)
magic_staff = Item("Magic Staff", "equipment", {"attack_power": 12, "intelligence": 3}, 100)

# Armor definitions
leather_armor = Item("Leather Armor", "equipment", {"armor": 5}, 40)
chainmail_armor = Item("Chainmail Armor", "equipment", {"armor": 10}, 80)
plate_armor = Item("Plate Armor", "equipment", {"armor": 15}, 120)

# Jewelry definitions
silver_ring = Item("Silver Ring", "equipment", {"mana": 10}, 30)
gold_necklace = Item("Gold Necklace", "equipment", {"health": 20}, 60)