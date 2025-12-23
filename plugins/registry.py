class PluginRegistry:
    def __init__(self):
        self.enemies = {}
        self.enemies_by_tier = {}

    def register_enemy(self, enemy_id, data):
        self.enemies[enemy_id] = data

        tier = data.get("tier")
        if tier:
            self.enemies_by_tier.setdefault(tier, []).append(data)

    def get_enemies_for_tier(self, tier):
        return self.enemies_by_tier.get(tier, [])

    def register_item(self, item_id, data):
        self.items[item_id] = data

    def get_enemy_data(self, enemy_id):
        return self.enemies.get(enemy_id)

    def get_item_data(self, item_id):
        return self.items.get(item_id)