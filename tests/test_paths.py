import unittest
import os
import shutil
from functions import get_data_dir, save_game


class PathsTests(unittest.TestCase):
    def test_get_data_dir_and_save_default(self):
        d = get_data_dir('python-game-test')
        self.assertTrue(os.path.exists(d))
        # save default - should create savegame.json inside this directory
        try:
            ok = save_game(None)
            # save_game without args writes to the app data dir for the default app name
            self.assertTrue(ok)
            # locate the default save path
            data_dir = get_data_dir()
            path = os.path.join(data_dir, 'savegame.json')
            self.assertTrue(os.path.exists(path))
        finally:
            try:
                os.remove(path)
            except Exception:
                pass


if __name__ == '__main__':
    unittest.main()
