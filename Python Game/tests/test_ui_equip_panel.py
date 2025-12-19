import unittest
import player
from player_helpers import equip_item, unequip_item
from items import iron_sword, leather_armor


class UIEquipPanelTests(unittest.TestCase):
    def test_equip_and_unequip_changes_player_equipment(self):
        p = player.player
        p['inventory'] = [iron_sword, leather_armor]
        p['equipment'] = {'weapon': None, 'armor': None, 'accessory': None}
        ok = equip_item(iron_sword)
        self.assertTrue(ok)
        self.assertEqual(p['equipment']['weapon'], iron_sword)
        # Now unequip
        res = unequip_item('weapon')
        self.assertTrue(res)
        self.assertIsNone(p['equipment']['weapon'])
        # ensure item back in inventory
        self.assertIn(iron_sword, p['inventory'])


if __name__ == '__main__':
    unittest.main()
