from character import characters
from location import locations


class User:

    def __init__(self, username):
        self.username = username
        self.character = None
        self.location = None
        self.subloc = None
        self.pos = "center"

    def set_from_msg(self, *args):
        args = list(args)
        self.location = locations[args[1]]
        self.subloc = self.location.get_sub(args[2])
        self.character = characters[args[3]]
        self.character.load()
        self.character.set_current_sprite(args[4])
        self.pos = self.set_pos(args[5])

    def set_char(self, char):
        self.character = char

    def set_loc(self, loc):
        self.location = loc

    def set_subloc(self, subloc):
        self.subloc = subloc

    def set_pos(self, pos):
        if self.pos is not None:
            if self.pos == 'right':
                self.subloc.set_r_user(None)
            elif self.pos == 'left':
                self.subloc.set_l_user(None)
            else:
                self.subloc.set_c_user(None)
        self.pos = pos

    def get_char(self):
        return self.character

    def get_loc(self):
        return self.location

    def get_subloc(self):
        return self.subloc

    def get_pos(self):
        return self.pos
