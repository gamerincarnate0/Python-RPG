import unittest
import player
from player_helpers import add_loot, equip_item
from items import iron_sword, steel_axe


class AutoEquipTests(unittest.TestCase):
    def setUp(self):
        p = player.player
        p['inventory'] = []
        p['equipment'] = {'weapon': None, 'armor': None, 'accessory': None}
        # reset bonuses
        p['attack_power_bonus'] = 0
        p['armor_bonus'] = 0

    def test_auto_equips_better_weapon(self):
        p = player.player
        # start with iron sword equipped
        p['inventory'].append(iron_sword)
        equip_item(iron_sword)
        self.assertEqual(p['equipment']['weapon'], iron_sword)

        # acquire a better steel axe
        add_loot([steel_axe])
        # steel_axe should be auto-equipped
        self.assertEqual(p['equipment']['weapon'], steel_axe)

    def test_does_not_auto_equip_worse_item(self):
        p = player.player
        # equip steel axe
        p['inventory'].append(steel_axe)
        equip_item(steel_axe)
        self.assertEqual(p['equipment']['weapon'], steel_axe)

        # acquire a worse iron sword
        add_loot([iron_sword])
        # should keep steel axe equipped and keep iron sword in inventory
        self.assertEqual(p['equipment']['weapon'], steel_axe)
        self.assertIn(iron_sword, p['inventory'])


if __name__ == '__main__':
    unittest.main()
