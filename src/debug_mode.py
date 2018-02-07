from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty
from kivy.app import App
from user import User
from character import characters
from random import randint


class DebugModePopup(ModalView):

    def __init__(self, **kwargs):
        super(DebugModePopup, self).__init__(**kwargs)


class UserCreationInterface(ModalView):

    username_input = ObjectProperty(None)
    character_input = ObjectProperty(None)
    location_input = ObjectProperty(None)
    sublocation_input = ObjectProperty(None)
    position_input = ObjectProperty(None)

    def __init__(self, caller, **kwargs):
        super(UserCreationInterface, self).__init__(**kwargs)
        self.caller = caller

    def create_random_username(self):
        suffix = randint(1, 50)
        username = "TestUser{}".format(suffix)
        self.username_input.text = username

    def use_current_character(self):
        user = App.get_running_app().get_user()
        self.character_input.text = user.get_char().name

    def use_current_location(self):
        user = App.get_running_app().get_user()
        self.location_input.text = user.get_loc().get_name()

    def use_current_sublocation(self):
        user = App.get_running_app().get_user()
        self.sublocation_input.text = user.get_subloc().get_name()

    def use_current_position(self):
        user = App.get_running_app().get_user()
        self.position_input.text = user.get_pos()

    def on_create(self):
        self.caller.create_user(self.username_input.text, self.character_input.text, self.location_input.text,
                                self.sublocation_input.text, self.position_input.text)
        self.dismiss()


class DebugModeInterface(BoxLayout):

    def __init__(self, **kwargs):
        super(DebugModeInterface, self).__init__(**kwargs)
        self.debug_mode = DebugMode()

    def open_user_creation(self):
        popup = UserCreationInterface(self)
        popup.open()

    def create_user(self, username, character, location, sublocation, position):
        self.debug_mode.create_user(username, character, location, sublocation, position)


class DebugMode:

    def __init__(self):
        self.created_users = {}

    def create_user(self, username, character_name, location_name, sublocation_name, position):
        user = User(username)
        self.created_users[username] = user
        self.add_character_to_user(user, character_name)
        self.add_location_to_user(user, location_name)
        self.add_sublocation_to_user(user, sublocation_name)
        self.add_position_to_user(user, position)
        ooc_window = App.get_running_app().get_main_screen().ooc_window
        ooc_window.add_user(user)

    def add_character_to_user(self, user, character_name):
        character = characters.get(character_name, None)
        user.set_char(character)
        character.load_without_icons()

    def add_location_to_user(self, user, location_name):
        user.set_loc(location_name, from_string=True)

    def add_sublocation_to_user(self, user, sublocation_name):
        location = user.get_loc()
        sublocation = location.get_sub(sublocation_name)
        user.set_subloc(sublocation)

    def add_position_to_user(self, user, position):
        user.set_pos(position)
