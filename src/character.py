from kivy.config import ConfigParser
from kivy.atlas import Atlas
import os


class Character:

    def __init__(self, name):
        self.name = name
        self.path = "characters/{0}/".format(self.name)
        self.config = ConfigParser(self.name)
        self.config.read(self.path + "settings.ini")
        char = self.config['character']
        self.display_name = char['name']
        self.series = char['series']
        self.sprites_path = self.path + char['sprites']
        self.icons_path = self.path + char['icons']
        self.avatar = self.path + "avatar.png"

    def load(self):
        self.sprites = Atlas(self.sprites_path)
        self.icons = Atlas(self.icons_path)


characters = {name: Character(name) for name in os.listdir("characters") if os.path.isdir("characters/" + name)}
series = ["OC"]
