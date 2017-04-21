from character import characters
from location import locations


class User:

    def __init__(self, username):
        self.username = username
        self.character = None
        self.location = None
        self.subloc = None
        self.pos = "center"
        self.current_sprite = None
        self.prev_subloc = None

    def set_from_msg(self, *args):
        args = list(args)
        self.location = locations[args[1]]
        self.subloc = self.location.get_sub(args[2])
        self.set_current_sprite(args[4])
        self.character = characters.get(args[3])
        if self.character is None:
            self.character = characters['RedHerring']
            self.set_current_sprite('4')
        self.character.load()
        self.set_pos(args[5])

    def set_current_sprite(self, id):
        self.current_sprite = id

    def get_current_sprite(self):
        return self.character.get_sprite(self.current_sprite)

    def set_char(self, char):
        self.character = char

    def set_loc(self, loc):
        self.location = loc

    def set_subloc(self, subloc):
        self.prev_subloc = self.subloc
        self.subloc = subloc

    def set_pos(self, pos):
        if self.pos is not None:
            if self.pos == 'right':
                if self.prev_subloc is not None and self.prev_subloc.get_r_user() is self:
                    self.prev_subloc.set_r_user(None)
                else:
                    self.subloc.set_r_user(None)
            elif self.pos == 'left':
                if self.prev_subloc is not None and self.prev_subloc.get_l_user() is self:
                    self.prev_subloc.set_l_user(None)
                else:
                    self.subloc.set_l_user(None)
            else:
                if self.prev_subloc is not None and self.prev_subloc.get_c_user() is self:
                    self.prev_subloc.set_c_user(None)
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
