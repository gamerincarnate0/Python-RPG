import unittest
from unittest.mock import patch
import player
from items import health_potion, iron_sword
from player_helpers import add_experience, add_gold, add_loot, use_health_potion, get_attack_power, attack_target


class PlayerHelpersTestCase(unittest.TestCase):
    def setUp(self):
        self.p = player.player
        # reset relevant fields
        self.p['level'] = 1
        self.p['experience'] = 0
        self.p['gold'] = 0
        self.p['inventory'] = []
        self.p['max_health'] = 100
        self.p['health'] = 40
        self.p['strength'] = 10
        self.p['inventory_capacity'] = 5

    def test_add_experience_and_level_up(self):
        # Grant more XP than needed for a level to force level-up
        threshold = player.calculate_experience_to_next_level(self.p['level'])
        add_experience(threshold + 5)
        self.assertGreater(self.p['level'], 1)
        self.assertLess(self.p['experience'], threshold + 5)

    def test_add_gold(self):
        add_gold(50)
        self.assertEqual(self.p['gold'], 50)

    def test_add_loot_and_capacity(self):
        add_loot([iron_sword])
        self.assertIn(iron_sword, self.p['inventory'])
        # fill inventory and try to add another
        self.p['inventory'] = [health_potion] * self.p['inventory_capacity']
        add_loot([iron_sword])
        # inventory should remain the same size
        self.assertEqual(len(self.p['inventory']), self.p['inventory_capacity'])

    def test_use_health_potion(self):
        # put potion in inventory and use it
        self.p['health'] = 10
        self.p['inventory'] = [health_potion]
        used = use_health_potion()
        self.assertTrue(used)
        self.assertGreater(self.p['health'], 10)

    def test_attack_target_damage(self):
        # deterministic attack by patching random.randint used inside get_attack_power
        class Dummy:
            def __init__(self):
                self.name = 'Dummy'
                self.health = 20
                self.armor = 1
            def take_damage(self, dmg):
                self.health -= dmg
        d = Dummy()
        with patch('random.randint', return_value=0):
            attack_target(d)
        # should have reduced health
        self.assertLess(d.health, 20)


if __name__ == '__main__':
    unittest.main()
