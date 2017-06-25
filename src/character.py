from kivy.config import ConfigParser
from kivy.atlas import Atlas
from kivy.uix.image import Image
import os


series_list = ["OC"]


class Character:

    def __init__(self, name):
        global series_list
        self.name = name
        self.path = "characters/{0}/".format(self.name)
        self.config = ConfigParser(self.name)
        self.config.read(self.path + "settings.ini")
        char = self.config['character']
        self.display_name = char['name']
        con_series = char['series']
        if con_series in series_list:
            self.series = con_series
        else:
            series_list.append(con_series)
            self.series = con_series

        self.sprites_path = self.path + char['sprites']
        self.icons_path = self.path + char['icons']
        self.avatar = self.path + "avatar.png"
        self.loaded = False
        self.sprites = None
        self.icons = None

    def load(self):
        if self.loaded:
            return
        self.sprites = "atlas://" + self.sprites_path[:-6] + "/"
        self.icons = Atlas(self.icons_path)
        self.loaded = True

    def get_icons(self):
        try:
            return self.icons
        except AttributeError:
            print("The icons aren't loaded into memory.")
            raise

    def get_sprite(self, num):
        try:
            return Image(source=self.sprites+num).texture
        except AttributeError:
            print("The sprites aren't loaded into memory.")
            raise

characters = {name: Character(name) for name in os.listdir("characters") if os.path.isdir("characters/" + name)}
