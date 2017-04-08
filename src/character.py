from kivy.config import ConfigParser


class Character:

    def __init__(self, name):
        self.name = name
        self.config = ConfigParser(self.name)
        self.config.read("characters/{0}/settings.ini".format(self.name))
