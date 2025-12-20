import unittest
from unittest.mock import patch
import main
import player
from items import iron_sword


class FakeParent:
    def __init__(self):
        self._destroyed = False
    def title(self):
        return 'Inventory'
    def destroy(self):
        self._destroyed = True
    def winfo_exists(self):
        return True

class FakeTooltip:
    def __init__(self, parent):
        self.master = parent
        self.closed = False
    def destroy(self):
        self.closed = True


class InventoryRefreshTests(unittest.TestCase):
    def setUp(self):
        self.p = player.player
        self.p['inventory'] = [iron_sword]
        self.p['equipment'] = {'weapon': None, 'armor': None, 'accessory': None}

    def test_equip_from_inventory_refreshes(self):
        parent = FakeParent()
        tooltip = FakeTooltip(parent)
        called = {'view': False}

        with patch('main.view_inventory_gui') as mock_view, patch('functions.TextFuncs.var_speed_print') as mock_print:
            mock_view.side_effect = lambda: called.__setitem__('view', True)
            main._equip_and_refresh_main(iron_sword, tooltip)

        # iron_sword should be equipped and removed from inventory
        self.assertEqual(self.p['equipment']['weapon'], iron_sword)
        self.assertNotIn(iron_sword, self.p['inventory'])
        # parent inventory should have been destroyed and view re-opened
        self.assertTrue(parent._destroyed)
        self.assertTrue(called['view'])
        # UI print should be called only once
        self.assertEqual(mock_print.call_count, 1)


if __name__ == '__main__':
    unittest.main()
