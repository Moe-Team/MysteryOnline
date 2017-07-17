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
        self.color = 'ffffff' # Default color for text
        self.colored = None # True for a color selected
        self.color_ids = ['ffffff', 'ff3333', '0000ff', 'ffd700', '00cd00', 'rainbow'] # Color code for text

    def set_from_msg(self, *args):
        args = list(args)
        self.location = locations[args[1]]
        self.set_subloc(self.location.get_sub(args[2]))
        self.set_current_sprite(args[4])
        self.character = characters.get(args[3])
        if self.character is None:
            self.character = characters['RedHerring']
            self.set_current_sprite('4')
        self.character.load(no_icons=True)
        self.set_pos(args[5])

    def get_color(self):
        return self.color

    def set_color(self, col):
        if col == 'red':
            self.color = 'ff3333'
        elif col == 'blue':
            self.color = '0000ff'
        elif col == 'golden':
            self.color = 'ffd700'
        elif col == 'green':
            self.color = '00cd00'
        elif col == 'FUCKING RAINBOW':
            self.color = 'rainbow'
        elif col == 'normal':
            self.color = 'ffffff'

    def set_current_sprite(self, num):
        self.current_sprite = num

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
                if self.prev_subloc is not None and self in self.prev_subloc.r_users:
                    self.prev_subloc.remove_r_user(self)
                elif self in self.subloc.r_users:
                    self.subloc.remove_r_user(self)
            elif self.pos == 'left':
                if self.prev_subloc is not None and self in self.prev_subloc.l_users:
                    self.prev_subloc.remove_l_user(self)
                elif self in self.subloc.l_users:
                    self.subloc.remove_l_user(self)
            else:
                if self.prev_subloc is not None and self in self.prev_subloc.c_users:
                    self.prev_subloc.remove_c_user(self)
                elif self in self.subloc.c_users:
                    self.subloc.remove_c_user(self)
        self.pos = pos

    def get_char(self):
        return self.character

    def get_loc(self):
        return self.location

    def get_subloc(self):
        return self.subloc

    def get_pos(self):
        return self.pos

    def remove(self):
        if self.pos is None or self.subloc is None:
            return
        if self.pos == 'right':
            self.subloc.remove_r_user(self)
        elif self.pos == 'left':
            self.subloc.remove_l_user(self)
        else:
            self.subloc.remove_c_user(self)