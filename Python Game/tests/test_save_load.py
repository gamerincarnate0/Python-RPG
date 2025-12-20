import unittest
import tempfile
import os
import player
from items import iron_sword, health_potion
from functions import save_game, load_game


class SaveLoadTests(unittest.TestCase):
    def setUp(self):
        self.p = player.player
        self.p['level'] = 3
        self.p['experience'] = 12
        self.p['health'] = 75
        self.p['inventory'] = [health_potion]
        self.p['equipment'] = {'weapon': iron_sword, 'armor': None, 'accessory': None}
        self.p['gold'] = 42

    def test_save_and_load_roundtrip(self):
        fd, path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        try:
            ok = save_game(path)
            self.assertTrue(ok)

            # mutate player then load back
            self.p['level'] = 1
            self.p['inventory'] = []
            self.p['equipment'] = {'weapon': None, 'armor': None, 'accessory': None}

            ok2 = load_game(path)
            self.assertTrue(ok2)

            # check fields restored
            self.assertEqual(self.p['level'], 3)
            self.assertIn(health_potion, self.p['inventory'])
            self.assertEqual(self.p['equipment']['weapon'], iron_sword)
            self.assertEqual(self.p['gold'], 42)
        finally:
            os.remove(path)


if __name__ == '__main__':
    unittest.main()
