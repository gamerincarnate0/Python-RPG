import unittest
from unittest.mock import patch
import combat
import main


class AutoSaveTests(unittest.TestCase):
    def test_save_called_on_combat_end(self):
        # Patch save_game where functions.save_game is imported
        with patch('functions.save_game') as mock_save:
            mock_save.return_value = True
            # create minimal player/enemy
            player = {'name': 'Tester', 'health': 10, 'max_health': 10}
            class DummyEnemy:
                def __init__(self):
                    self.name = 'Dummy'
                    self.health = 0
                def is_alive(self):
                    return False
            e = DummyEnemy()
            c = combat.Combat(player, e)
            c._end_combat(True)
            mock_save.assert_called()

    def test_on_exit_calls_save_and_destroy(self):
        with patch('main.save_game') as mock_save:
            mock_save.return_value = True
            destroyed = {'called': False}

            # replace window.destroy temporarily
            orig_destroy = main.window.destroy
            try:
                main.window.destroy = lambda: destroyed.__setitem__('called', True)
                main.on_exit()
            finally:
                main.window.destroy = orig_destroy

            mock_save.assert_called()
            self.assertTrue(destroyed['called'])


if __name__ == '__main__':
    unittest.main()
