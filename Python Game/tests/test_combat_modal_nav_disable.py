import unittest
from unittest.mock import patch
import main


class CombatModalNavTests(unittest.TestCase):
    def test_nav_disabled_during_combat_and_reenabled_after_end(self):
        captured = {}

        def fake_start_gui(self_obj, parent, on_end=None, on_refresh=None):
            # record the callbacks so test can invoke them
            captured['on_end'] = on_end
            captured['on_refresh'] = on_refresh
            # ensure parent exists
            self_obj.win = parent

        class FakeFrame:
            def pack(self, *a, **k):
                return None
            def after(self, delay, fn):
                # don't actually schedule; just store for test if needed
                try:
                    fn()
                except Exception:
                    pass

        with patch('combat.Combat.start_gui', new=fake_start_gui), patch('functions.TextFuncs.var_speed_print'), patch('main.disable_nav') as mock_disable, patch('main.tk.Frame', new=lambda *a, **k: FakeFrame()):
            # start combat; this should call disable_nav(True) and invoke Combat.start_gui
            main.start_combat()

            mock_disable.assert_any_call(True)

            # simulate combat end via the captured callback
            self.assertIn('on_end', captured)
            captured['on_end'](True)

            # on_combat_end should call disable_nav(False)
            mock_disable.assert_any_call(False)


if __name__ == '__main__':
    unittest.main()
