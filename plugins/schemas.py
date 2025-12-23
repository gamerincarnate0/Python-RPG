REQUIRED_ENEMY_FIELDS = {
    "id": str,
    "name": str,
    "health": int,
    "attack_power": int,
    "armor": int,
    "tier": int
}

REQUIRED_ITEM_FIELDS = {
    "id": str,
    "name": str,
    "item_type": str,
    "effect": str,
    "value": int,
    "rarity": str
}

def validate_enemy(data: dict):
    for field, field_type in REQUIRED_ENEMY_FIELDS.items():
        if field not in data:
            raise ValueError(f"Missing field '{field}'")
        if not isinstance(data[field], field_type):
            raise ValueError(f"Field '{field}' must be {field_type.__name__}")

def validate_item(data: dict):
    for field, field_type in REQUIRED_ITEM_FIELDS.items():
        if field not in data:
            raise ValueError(f"Missing field '{field}'")
        if not isinstance(data[field], field_type):
            raise ValueError(f"Field '{field}' must be {field_type.__name__}")