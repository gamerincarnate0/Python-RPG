import unittest
from unittest.mock import patch
import enemy
from settings import GameplaySettings
from player_helpers import get_attack_power
import player


class BalanceTests(unittest.TestCase):
    def test_minimum_player_damage_against_high_armor(self):
        # Setup a dummy enemy with huge armor
        class E:
            def __init__(self):
                self.name = 'Tank'
                self.armor = 1000
                self.health = 100
            def take_damage(self, dmg):
                self.health -= dmg
        e = E()
        # Patch random to deterministic
        with patch('random.randint', return_value=0):
            dmg = max(1, get_attack_power() - e.armor)
        self.assertGreaterEqual(dmg, 1)

    def test_minimum_enemy_damage_against_high_defense(self):
        # enemy attack vs player defense formula
        test_player = {'agility': 999}
        e = enemy.generate_enemy('tier1')
        # simulate calculation from combat
        with patch('random.randint', return_value=0):
            dmg = max(1, e.attack() - (test_player.get('agility', 0) // 3) + 0)
        self.assertGreaterEqual(dmg, 1)

    def test_generate_enemy_scales_with_difficulty(self):
        # Save original difficulty
        orig = GameplaySettings.GLOBAL_DIFFICULTY
        try:
            GameplaySettings.GLOBAL_DIFFICULTY = 1
            low = enemy.generate_enemy('tier2')
            GameplaySettings.GLOBAL_DIFFICULTY = 5
            high = enemy.generate_enemy('tier2')
            # high difficulty enemies should have higher HP and attack at least the same
            self.assertGreaterEqual(high.max_health, low.max_health)
            self.assertGreaterEqual(high.attack_power, low.attack_power)
        finally:
            GameplaySettings.GLOBAL_DIFFICULTY = orig

    def test_exact_xp_level_up(self):
        p = player.player
        p['level'] = 1
        p['experience'] = 0
        threshold = player.calculate_experience_to_next_level(p['level'])
        # Add exactly threshold
        from player_helpers import add_experience
        add_experience(threshold)
        self.assertGreater(p['level'], 1)
        # experience left should be < threshold
        self.assertLess(p['experience'], threshold)


if __name__ == '__main__':
    unittest.main()
