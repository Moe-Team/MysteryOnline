import os

from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.config import ConfigParser


class SubLocation:

    def __init__(self, name, img_path):
        self.name = name
        self.img_path = img_path
        self.foreground_path: str = None

        dir_path: str = os.path.dirname(img_path)
        foreground_png: str = os.path.join(dir_path, name+"_foreground.png")  # We only support png

        if os.path.exists(foreground_png):
            self.foreground_path = foreground_png

        self.c_users = []
        self.l_users = []
        self.r_users = []
        self.o_users = []

    def get_img(self):
        return Image(source=self.img_path)

    def get_foreground_img(self):
        return Image(source=self.foreground_path)

    def has_foreground(self) -> bool:
        return self.foreground_path is not None

    def get_name(self):
        return self.name

    def add_o_user(self, user):
        self.o_users.append(user)

    def add_c_user(self, user):
        self.c_users.append(user)

    def add_l_user(self, user):
        self.l_users.append(user)

    def add_r_user(self, user):
        self.r_users.append(user)

    def get_c_user(self):
        return self.c_users[-1]

    def get_l_user(self):
        return self.l_users[-1]

    def get_r_user(self):
        return self.r_users[-1]

    def get_o_user(self):
        return self.o_users[-1]

    def remove_o_user(self, user):
        if user in self.o_users:
            self.o_users.remove(user)

    def remove_c_user(self, user):
        if user in self.c_users:
            self.c_users.remove(user)

    def remove_l_user(self, user):
        if user in self.l_users:
            self.l_users.remove(user)

    def remove_r_user(self, user):
        if user in self.r_users:
            self.r_users.remove(user)


class LocationManager:

    def __init__(self):
        self.locations = {}
        self.is_loaded = False

    def load_locations(self):
        if self.is_loaded:
            return
        self.locations = {name: Location(name)
                          for name in os.listdir("locations") if os.path.isdir("locations/" + name)}
        for location_name in self.locations:
            self.locations[location_name].load()
        self.is_loaded = True

    def get_locations(self):
        self.ensure_loaded()
        return self.locations

    def ensure_loaded(self):
        if not self.is_loaded:
            self.load_locations()

    def has_location(self, location_name: str):
        self.ensure_loaded()
        return location_name in self.locations


class Location:

    def __init__(self, name, directory="locations"):
        self.name = name
        self.path = "{0}/{1}/".format(directory, self.name)
        self.sublocations = {}
        self.placeholder_subloc = SubLocation('Missingno',  "misc_img/Missingno.jpg")

    def load(self):
        for file in os.listdir(self.path):
            strip: str = self.strip_ext(file)
            if strip.endswith("_foreground"):
                continue
            self.sublocations[strip] = SubLocation(strip, self.path+file)

    @staticmethod
    def strip_ext(name: str) -> str:
        # Strips extension from sublocation names
        if name.lower().endswith((".jpg", ".png")):
            return name[:-4]

    def list_sub(self):
        return sorted(list(self.sublocations.keys()))

    def get_sub(self, name) -> SubLocation:
        return self.sublocations[name]

    def get_first_sub(self) -> str:
        config = ConfigParser()
        config.read('mysteryonline.ini')
        try:
            return self.sublocations[str(config.get('other', 'last_sublocation'))].name
        except KeyError:
            return self.get_real_first_sub()

    def get_real_first_sub(self) -> str:
        return self.list_sub()[0]

    def get_name(self):
        return self.name


location_manager = LocationManager()
