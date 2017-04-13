

class User:

    def __init__(self, username):
        self.username = username
        self.character = None
        self.location = None

    def set_char(self, char):
        self.character = char

    def set_loc(self, loc):
        self.location = loc

    def get_char(self):
        return self.character

    def get_loc(self):
        return self.location
