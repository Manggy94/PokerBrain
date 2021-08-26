import unittest
from API.Table import *


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player("Jean", 3, 2000)

    def test_player_instance_is_good(self):
        self.assertIsInstance(self.player, Player)

    def test_player_name(self):
        self.assertGreater(len(self.player.name), 0)
        self.assertLess(len(self.player.name), 12)
        self.assertIsInstance(self.player.name, str)

    def test_player_stack(self):
        self.assertGreater(self.player.stack, 0)




if __name__ == '__main__':
    unittest.main()
