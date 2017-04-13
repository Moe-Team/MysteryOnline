import os
from kivy.uix.image import Image


class Location:

    def __init__(self, name):
        self.name = name
        self.path = "locations/{0}/".format(self.name)
        self.sublocations = {}

    def load(self):
        self.sublocations = {file: Image(source=self.path+file) for file in os.listdir(self.path)}

    def list_sub(self):
        return sorted(list(self.sublocations.keys()))

    def get_sub(self, name):
        return self.sublocations[name]

    def get_first_sub(self):
        return self.list_sub()[0]


locations = {'Hakuryou': Location('Hakuryou')}
