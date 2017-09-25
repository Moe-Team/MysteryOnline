from kivy.config import ConfigParser
from kivy.atlas import Atlas
from icarus import Icarus
import os


series_list = ["OC"]


class Character:

    def __init__(self, name):
        self.name = name
        self.path = "characters/{0}/".format(self.name)
        self.display_name = None
        self.series = None
        self.sprites_path = None
        self.icons_path = None
        self.avatar = None
        self.loaded_sprites = False
        self.loaded_icons = False
        self.sprites = None
        self.icons = None
        self.config = ConfigParser(self.name)
        self.read_config()

    def read_config(self):
        global series_list
        self.config.read(self.path + "settings.ini")
        char = self.config['character']
        self.display_name = char['name']
        con_series = char['series']
        if con_series not in series_list:
            series_list.append(con_series)
        self.series = con_series
        self.sprites_path = self.path + char['sprites']
        self.icons_path = self.path + char['icons']
        self.avatar = self.path + "avatar.png"

    def load(self):
        if self.loaded_icons and self.loaded_sprites:
            return
        if not self.loaded_sprites:
            self.load_sprites()
        if not self.loaded_icons:
            self.load_icons()

    def load_icons(self):
        self.icons = Atlas(self.icons_path)
        self.loaded_icons = True

    def load_sprites(self):
        self.sprites = Icarus(self.sprites_path)
        self.loaded_sprites = True

    def load_without_icons(self):
        if not self.loaded_sprites:
            self.load_sprites()

    def get_icons(self):
        try:
            return self.icons
        except AttributeError:
            print("The icons aren't loaded into memory.")
            raise

    def get_sprite(self, num):
        try:
            return self.sprites[num]
        except AttributeError:
            print("The sprites aren't loaded into memory.")
            raise


characters = {name: Character(name) for name in os.listdir("characters") if os.path.isdir("characters/" + name)}
