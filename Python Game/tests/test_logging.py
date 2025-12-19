import unittest
import os
import enemy
import player
from combat import Combat


class LoggingTests(unittest.TestCase):
    def setUp(self):
        # ensure no log exists
        try:
            os.remove('combat_log.txt')
        except FileNotFoundError:
            pass

    def test_end_combat_writes_log(self):
        e = enemy.generate_enemy('tier1')
        c = Combat(player.player, e)
        # Call _end_combat in non-GUI mode
        c._end_combat(True)
        self.assertTrue(os.path.exists('combat_log.txt'))
        with open('combat_log.txt', 'r', encoding='utf-8') as fh:
            contents = fh.read()
        self.assertIn('Victory vs', contents)

    def tearDown(self):
        try:
            os.remove('combat_log.txt')
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    unittest.main()
