from icarus import Icarus
from kivy.app import App
from kivy.uix.button import Button
from kivy.clock import Clock
import json
import os
import random
import unittest


PATH_PREFIX = "characters/"
PATH_SPRITE_SUFFIX = "/sprites.atlas"
PATH_ICON_SUFFIX = "/icons.atlas"


class TestButton(Button):

    def __init__(self, **kwargs):
        super(TestButton, self).__init__(**kwargs)
        Clock.schedule_once(self.ready)

    def ready(self, *args):
        app = App.get_running_app()
        app.stop()


class TestApp(App):

    def build(self):
        return TestButton(text="Just testing")


class IcarusTests(unittest.TestCase):

    def setUp(self):
        TestApp().run()
        os.chdir("../src")
        self.characters = [name for name in os.listdir("characters")]

    def test_load_file(self):
        for char in self.characters:
            path = PATH_PREFIX + char + PATH_SPRITE_SUFFIX
            test_sprites = Icarus(path)
            self.assertEqual(path, test_sprites.filename)
            self.assertEqual({}, test_sprites.textures)

    # pretty slow
    # def test_load_first_and_last_sprite(self):
    #     for char in self.characters:
    #         path = PATH_PREFIX + char + PATH_SPRITE_SUFFIX
    #         first_icon = self.pick_first_icon(path)
    #         last_icon = self.pick_last_icon(path)
    #         test_sprites = Icarus(path)
    #         test_sprites.load(first_icon)
    #         self.assertNotEqual({}, test_sprites.textures)
    #         self.assertIn(first_icon, test_sprites.textures)
    #         test_sprites.load(last_icon)
    #         self.assertNotEqual({}, test_sprites.textures)
    #         self.assertIn(last_icon, test_sprites.textures)

    # will eat a lot of memory if you use it on too many characters
    # def test_ten_random_sprites(self):
    #     for char in self.characters[47:]:
    #         path = PATH_PREFIX + char + PATH_SPRITE_SUFFIX
    #         print("Checking character: ", char)
    #         test_sprites = Icarus(path)
    #         for _ in range(10):
    #             random_icon = self.pick_random_icon(path)
    #             print("Checking sprite: ", random_icon)
    #             test_sprites.load(random_icon)
    #             self.assertNotEqual({}, test_sprites.textures)
    #             self.assertIn(random_icon, test_sprites.textures)

    # will eat a lot of memory if you use it on too many characters
    # def test_all_sprites(self):
    #     for char in self.characters[80:]:
    #         path = PATH_PREFIX + char + PATH_SPRITE_SUFFIX
    #         print("Checking character: ", char)
    #         test_sprites = Icarus(path)
    #         sprites = self.get_all_sprites(path)
    #         for sprite in sprites:
    #             test_sprites.load(sprite)
    #             self.assertNotEqual({}, test_sprites.textures)
    #             self.assertIn(sprite, test_sprites.textures)

    def pick_first_icon(self, path):
        meta, subs = self.extract_and_sort_subfiles(path)
        first_sub = meta[subs[0]]
        first_sub = sorted(first_sub)
        return first_sub[0]

    def pick_last_icon(self, path):
        meta, subs = self.extract_and_sort_subfiles(path)
        last_sub = meta[subs[-1]]
        last_sub = sorted(last_sub, reverse=True)
        return last_sub[0]

    def pick_random_icon(self, path):
        meta, subs = self.extract_and_sort_subfiles(path)
        random_sub = random.choice(subs)
        random_sub = meta[random_sub]
        random_sub = list(random_sub.keys())
        random_icon = random.choice(random_sub)
        return random_icon

    def get_all_sprites(self, path):
        meta, subs = self.extract_and_sort_subfiles(path)
        sprites = []
        for sub in meta:
            sprite_dict = meta[sub]
            for sprite in sprite_dict:
                sprites.append(sprite)
        return sprites

    def extract_and_sort_subfiles(self, path):
        with open(path, 'r') as fd:
            meta = json.load(fd)
        subs = list(meta.keys())
        subs = sorted(subs)
        return meta, subs


if __name__ == "__main__":
    unittest.main()
