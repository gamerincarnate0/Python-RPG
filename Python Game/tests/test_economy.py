import unittest
from items import iron_sword
import player
from player_helpers import equip_item, unequip_item, sell_item


class EconomyTests(unittest.TestCase):
    def setUp(self):
        p = player.player
        p['inventory'] = [iron_sword]
        p['gold'] = 0
        p['equipment'] = {'weapon': None, 'armor': None, 'accessory': None}
        p['attack_power_bonus'] = 0

    def test_equip_item_moves_to_slot_and_adds_bonus(self):
        p = player.player
        self.assertIn(iron_sword, p['inventory'])
        ok = equip_item(iron_sword)
        self.assertTrue(ok)
        self.assertNotIn(iron_sword, p['inventory'])
        self.assertEqual(p['equipment']['weapon'], iron_sword)
        self.assertGreater(p['attack_power_bonus'], 0)

    def test_sell_item_from_inventory(self):
        p = player.player
        # put a second iron sword into inventory and sell it
        p['inventory'] = [iron_sword]
        gold = sell_item(iron_sword)
        self.assertGreater(gold, 0)
        self.assertEqual(p['gold'], gold)
        self.assertNotIn(iron_sword, p['inventory'])

    def test_sell_equipped_item(self):
        p = player.player
        p['inventory'] = [iron_sword]
        equip_item(iron_sword)
        # now sell (should unequip then sell)
        gold = sell_item(iron_sword)
        self.assertGreater(gold, 0)
        self.assertEqual(p['gold'], gold)
        self.assertIsNone(p['equipment']['weapon'])


if __name__ == '__main__':
    unittest.main()
