import unittest
import combat
import main
from items import iron_sword, plate_armor


class UIEmojisTests(unittest.TestCase):
    def test_message_icon_for_hit(self):
        icon = combat.message_icon('You hit the Goblin for 3 damage')
        self.assertIn('⚔️', icon)

    def test_message_icon_respects_rarity(self):
        icon = combat.message_icon('Found loot: Plate Armor', rarity='epic')
        self.assertEqual(icon, '🌟')

    def test_format_equipment_text_includes_slot_and_rarity(self):
        txt = main.format_equipment_text('weapon', iron_sword)
        self.assertIn('⚔️', txt)
        self.assertIn('✨', txt)  # iron_sword is uncommon -> ✨
        txt2 = main.format_equipment_text('armor', plate_armor)
        self.assertIn('🛡️', txt2)
        self.assertIn('🌟', txt2)  # plate_armor is epic -> 🌟


if __name__ == '__main__':
    unittest.main()
