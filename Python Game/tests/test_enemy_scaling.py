import unittest
from enemy import generate_enemy_for_player


class EnemyScalingTests(unittest.TestCase):
    def test_scaling_with_player_level(self):
        e1 = generate_enemy_for_player(1)
        e10 = generate_enemy_for_player(10)

        # Ensure higher-level enemy has greater or equal stats
        self.assertGreaterEqual(e10.max_health, e1.max_health)
        self.assertGreaterEqual(e10.attack_power, e1.attack_power)
        self.assertGreaterEqual(e10.armor, e1.armor)

    def test_tier_mapping_boundaries(self):
        # Check that boundary levels map to expected tiers implicitly by health jumps
        e3 = generate_enemy_for_player(3)
        e4 = generate_enemy_for_player(4)
        # Expect e4 to be at least as tough as e3
        self.assertGreaterEqual(e4.max_health, e3.max_health)


if __name__ == '__main__':
    unittest.main()
