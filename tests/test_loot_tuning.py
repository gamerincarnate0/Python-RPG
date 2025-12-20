import unittest
from unittest.mock import patch
import enemy
from items import health_potion, iron_sword
from settings import GameplaySettings


class LootTuningTests(unittest.TestCase):
    def test_items_have_rarity(self):
        self.assertTrue(hasattr(health_potion, 'rarity'))
        self.assertTrue(hasattr(iron_sword, 'rarity'))

    def test_difficulty_multiplier_behavior(self):
        # baseline
        GameplaySettings.GLOBAL_DIFFICULTY = 1
        m_low = enemy.get_difficulty_multiplier()
        GameplaySettings.GLOBAL_DIFFICULTY = 5
        m_high = enemy.get_difficulty_multiplier()
        self.assertGreater(m_high, m_low)

    def test_loot_selection_with_weighted_choices(self):
        # Force a drop by making random.random small, and force random.choices to pick iron_sword
        with patch('random.random', return_value=0.01):
            with patch('random.choices', return_value=[iron_sword]):
                e = enemy.generate_enemy('tier1')
                self.assertTrue(len(e.loot) >= 1)
                self.assertEqual(e.loot[0], iron_sword)


if __name__ == '__main__':
    unittest.main()
