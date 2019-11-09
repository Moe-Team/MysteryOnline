import unittest
from MysteryOnline.sprite_organizer import SpriteOrganizer


class MockSprite:

        def __init__(self, name):
            self.name = name


class SpriteTest(unittest.TestCase):

    def setUp(self):
        self.so = SpriteOrganizer()

    def test_add_sprites(self):
        self.so.add_sprite(MockSprite("1"))
        self.so.add_sprite(MockSprite("2"))
        self.assertEqual(2, len(self.so.get_sprites()))

    def test_sprites_sorted(self):
        ms1 = MockSprite("1")
        ms2 = MockSprite("2")
        ms3 = MockSprite("3")
        self.so.add_sprite(ms1)
        self.so.add_sprite(ms2)
        self.so.add_sprite(ms3)
        self.assertIs(ms3, self.so.get_sprites()[0])
        self.assertIs(ms2, self.so.get_sprites()[1])
        self.assertIs(ms1, self.so.get_sprites()[2])

    def test_same_sprite_readded(self):
        ms1 = MockSprite("1")
        ms2 = MockSprite("2")
        ms3 = MockSprite("3")
        self.so.add_sprite(ms1)
        self.so.add_sprite(ms2)
        self.so.add_sprite(ms3)
        self.so.add_sprite(ms1)
        self.assertEqual(3, len(self.so.get_sprites()))
        self.assertIs(ms1, self.so.get_sprites()[0])
        self.assertIs(ms3, self.so.get_sprites()[1])
        self.assertIs(ms2, self.so.get_sprites()[2])


if __name__ == '__main__':
    unittest.main()
