import os
from kivy.uix.image import AsyncImage


class SubLocation:

    def __init__(self, name, img):
        self.name = name
        self.img = img
        self.c_user = None
        self.l_user = None
        self.r_user = None

    def get_img(self):
        return self.img

    def get_name(self):
        return self.name

    def set_c_user(self, user):
        self.c_user = user

    def set_l_user(self, user):
        self.l_user = user

    def set_r_user(self, user):
        self.r_user = user

    def get_c_user(self):
        return self.c_user

    def get_l_user(self):
        return self.l_user

    def get_r_user(self):
        return self.r_user


class Location:

    def __init__(self, name):
        self.name = name
        self.path = "locations/{0}/".format(self.name)
        self.sublocations = {}

    def load(self):
        self.sublocations = {self.strip_ext(file):
            SubLocation(self.strip_ext(file), AsyncImage(source=self.path+file)) for file in os.listdir(self.path)}

    def strip_ext(self, name):
        # Strips extension from sublocation names
        if name.lower().endswith((".jpg", ".png")):
            return name[:4]

    def list_sub(self):
        return sorted(list(self.sublocations.keys()))

    def get_sub(self, name):
        return self.sublocations[name]

    def get_first_sub(self):
        return self.list_sub()[0]


locations = {'Hakuryou': Location('Hakuryou')}
