import unittest
import enemy
import combat


class PreventRecombatTests(unittest.TestCase):
    def test_enemy_is_fightable_true_false(self):
        e = enemy.generate_enemy('tier1')
        self.assertTrue(combat.enemy_is_fightable(e))
        e.health = 0
        self.assertFalse(combat.enemy_is_fightable(e))


if __name__ == '__main__':
    unittest.main()
