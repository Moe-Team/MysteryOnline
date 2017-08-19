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


class Location:

    def __init__(self, name):
        self.name = name
        self.path = "locations/{0}/".format(self.name)
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
        return self.sublocations[name]

    def get_first_sub(self):
        return self.list_sub()[0]


locations = {name: Location(name) for name in os.listdir("locations") if os.path.isdir("locations/" + name)}
