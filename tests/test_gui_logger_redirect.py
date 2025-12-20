import unittest
from functions import TextFuncs
import main


class GuiLoggerRedirectTests(unittest.TestCase):
    def test_var_speed_print_uses_registered_gui_logger(self):
        # Save and restore any existing GUI logger
        old = TextFuncs._gui_logger
        try:
            captured = {}

            def fake_logger(text, rarity=None):
                captured['text'] = text
                captured['rarity'] = rarity

            TextFuncs.set_gui_logger(fake_logger)

            TextFuncs.var_speed_print('Test GUI message.', 0, 0)

            self.assertIn('Test GUI message.', captured.get('text', ''))
        finally:
            TextFuncs.set_gui_logger(old)


if __name__ == '__main__':
    unittest.main()
