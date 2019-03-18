from kivy.config import ConfigParser
from kivy.atlas import Atlas
from kivy.logger import Logger
from icarus import Icarus
from kivy.app import App
import os


main_series_list = ["OC"]
extra_series_list = []


class Character:

    def __init__(self, name):
        self.name = name
        self.path = "characters/{0}/".format(self.name)
        self.display_name = None
        self.series = None
        self.extra_series = []
        self.sprites_path = None
        self.icons_path = None
        self.avatar = None
        self.loaded_sprites = False
        self.loaded_icons = False
        self.sprites = None
        self.icons = None
        self.link = None
        # Hash tables for faster membership checking
        self.nsfw_sprites = {}
        self.spoiler_sprites = {}
        self.cg_sprites = {}
        try:
            self.config = ConfigParser(self.name)
        except ValueError:
            self.config = ConfigParser.get_configparser(self.name)
        self.read_config()

    def read_config(self):
        global main_series_list
        self.config.read(self.path + "settings.ini")
        char = self.config['character']
        self.display_name = char['name']
        con_series = char['series']
        con_series = con_series.split(',')
        con_series = [s.strip() for s in con_series]
        main_series = con_series[0]
        if len(con_series) > 1:
            extra_series = con_series[1:]
            self.extra_series = extra_series
        if main_series not in main_series_list:
            main_series_list.append(main_series)
        for s in self.extra_series:
            if s not in extra_series_list:
                extra_series_list.append(s)
        self.series = main_series
        self.sprites_path = self.path + char['sprites']
        self.icons_path = self.path + char['icons']
        self.avatar = self.path + "avatar.png"
        self.read_nsfw_sprites()
        self.read_spoiler_sprites()
        self.read_cg_sprites()
        try:
            self.link = char['download']
        except KeyError:
            self.link = "no link"

    def read_nsfw_sprites(self):
        try:
            nsfw_list = self.config['nsfw']['sprites']
        except KeyError:
            return
        nsfw_list = nsfw_list.split(',')
        for sprite_name in nsfw_list:
            self.nsfw_sprites[sprite_name] = None

    def read_spoiler_sprites(self):
        try:
            spoiler_section = self.config['spoiler']
        except KeyError:
            return
        spoiler_list = []
        series = self.extra_series[:]
        series.insert(0, self.series)
        config = ConfigParser()
        config.read('mysteryonline.ini')
        try:
            whitelist = config.get('other', 'whitelisted_series')
        except:
            for key, s in zip(sorted(spoiler_section), series):
                spoiler_sprites = spoiler_section[key].split(',')
                spoiler_list.extend(spoiler_sprites)
            for sprite_name in spoiler_list:
                self.spoiler_sprites[sprite_name] = None
            return
        whitelist = whitelist.strip('[]')
        whitelist = whitelist.replace("'", "")
        whitelist = whitelist.split(',')
        whitelist = [x.strip() for x in whitelist]
        for key, s in zip(sorted(spoiler_section), series):
            if s not in whitelist:
                spoiler_sprites = spoiler_section[key].split(',')
                spoiler_list.extend(spoiler_sprites)
        for sprite_name in spoiler_list:
            self.spoiler_sprites[sprite_name] = None

    def read_cg_sprites(self):
        try:
            cg_list = self.config['CG']['sprites']
        except KeyError:
            return
        cg_list = cg_list.split(',')
        for sprite_name in cg_list:
            self.cg_sprites[sprite_name] = None

    def get_display_name(self):
        return self.display_name

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
            Logger.error("Icons: The icons aren't loaded into memory")
            raise

    def get_sprite(self, sprite_name):
        try:
            sprite = self.sprites[sprite_name]
            config = App.get_running_app().config
            if config.getdefaultint('other', 'nsfw_mode', 1) and sprite_name in self.nsfw_sprites:
                sprite.set_nsfw()
            elif config.getdefaultint('other', 'spoiler_mode', 1) and sprite_name in self.spoiler_sprites:
                sprite.set_spoiler()
            elif sprite_name in self.cg_sprites:
                sprite.set_cg()
            else:
                sprite.unset_nsfw()
                sprite.unset_spoiler()
            return sprite
        except AttributeError:
            Logger.error("Sprites: The sprites aren't loaded into memory")
            raise

    def get_spoiler_icons(self):
        return self.spoiler_sprites


characters = {name: Character(name) for name in os.listdir("characters") if os.path.isdir("characters/" + name)}
