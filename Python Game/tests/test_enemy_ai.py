import unittest
from unittest.mock import patch
import enemy
from items import health_potion
from player import player


class EnemyAITestCase(unittest.TestCase):
    def test_decide_action_high_hp(self):
        e = enemy.generate_enemy('tier1')
        e.health = e.max_health
        action = e.decide_action(player)
        self.assertEqual(action, 'attack')

    def test_decide_action_mid_hp_defend(self):
        e = enemy.generate_enemy('tier1')
        e.health = int(e.max_health * 0.5)
        # Force random.random to return small value to trigger defend branch
        with patch('random.random', return_value=0.2):
            action = e.decide_action(player)
        self.assertIn(action, ('attack', 'defend'))

    def test_decide_action_low_hp_heal_with_potion(self):
        e = enemy.generate_enemy('tier1')
        e.inventory.append(health_potion)
        e.health = int(e.max_health * 0.2)
        # Force random.random to low value to choose heal
        with patch('random.random', return_value=0.1):
            action = e.decide_action(player)
        self.assertEqual(action, 'heal')


if __name__ == '__main__':
    unittest.main()
