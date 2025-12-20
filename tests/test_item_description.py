import unittest
from items import health_potion, iron_sword


class ItemDescriptionTest(unittest.TestCase):
    def test_description_contains_expected_fields(self):
        d = health_potion.description()
        self.assertIn('Name: Health Potion', d)
        self.assertIn('Type: consumable', d)
        self.assertIn('Rarity: common', d)

        d2 = iron_sword.description()
        self.assertIn('Name: Iron Sword', d2)
        self.assertIn('Type: equipment', d2)
        self.assertIn('attack_power', d2)  # effect line


if __name__ == '__main__':
    unittest.main()
