import unittest
import os
import enemy
import player
from combat import Combat
from items import plate_armor


class RarityUITests(unittest.TestCase):
    def setUp(self):
        try:
            from functions import get_data_dir
            os.remove(os.path.join(get_data_dir(), 'combat_log.txt'))
        except FileNotFoundError:
            pass

    def test_loot_rarity_in_log(self):
        e = enemy.generate_enemy('tier1')
        # give a guaranteed epic item
        e.loot = [plate_armor]
        c = Combat(player.player, e)
        c._end_combat(True)
        from functions import get_data_dir
        with open(os.path.join(get_data_dir(), 'combat_log.txt'), 'r', encoding='utf-8') as fh:
            content = fh.read()
        self.assertIn('(epic)', content)

    def tearDown(self):
        try:
            from functions import get_data_dir
            os.remove(os.path.join(get_data_dir(), 'combat_log.txt'))
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    unittest.main()
