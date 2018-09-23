import os
from kivy.uix.image import Image


class SubLocation:

    def __init__(self, name, img_path):
        self.name = name
        self.img_path = img_path
        self.c_users = []
        self.l_users = []
        self.r_users = []

    def get_img(self):
        return Image(source=self.img_path)

    def get_name(self):
        return self.name

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
        if not self.is_loaded:
            self.load_locations()
        return self.locations


class Location:

    def __init__(self, name, directory="locations"):
        self.name = name
        self.path = "{0}/{1}/".format(directory, self.name)
        self.sublocations = {}

    def load(self):
        self.sublocations = {self.strip_ext(file):
                             SubLocation(self.strip_ext(file),
                                         self.path+file) for file in os.listdir(self.path)}

    def strip_ext(self, name):
        # Strips extension from sublocation names
        if name.lower().endswith((".jpg", ".png")):
            return name[:-4]

    def list_sub(self):
        return sorted(list(self.sublocations.keys()))

    def get_sub(self, name):
        if name != 'Missingno':
            return self.sublocations[name]
        else:
            missing_no = SubLocation('Missingno',  "misc_img/Missingno.jpg")
            return missing_no

    def get_first_sub(self):
        return self.list_sub()[0]

    def get_name(self):
        return self.name


location_manager = LocationManager()
