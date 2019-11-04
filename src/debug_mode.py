from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.app import App
from user import User
from character import characters
from random import randint, choice
from functools import partial


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


class UserManagementInterface(ModalView):

    message_input = ObjectProperty(None)
    sprite_input = ObjectProperty(None)
    delay_input = ObjectProperty(None)
    user_dropdown_button = ObjectProperty(None)

    def __init__(self, caller, **kwargs):
        super(UserManagementInterface, self).__init__(**kwargs)
        self.caller = caller
        self.dropdown = DropDown(scroll_type=["bars", "content"], effect_cls="ScrollEffect", bar_width=10)

    def ready(self):
        users = self.caller.debug_mode.get_created_users()
        for username in users:
            user = users[username]
            btn = Button(text=user.username, size_hint_y=None, height=40)
            btn.bind(on_release=lambda b: self.dropdown.select(b.text))
            self.dropdown.add_widget(btn)
        self.user_dropdown_button.bind(on_release=self.dropdown.open)
        self.dropdown.bind(on_select=lambda instance, x: setattr(self.user_dropdown_button, 'text', x))

    def send_message(self):
        self.caller.send_message(self.user_dropdown_button.text, self.message_input.text, self.sprite_input.text,
                                 self.delay_input.text)
        self.dismiss()


class DebugModeInterface(BoxLayout):

    def __init__(self, **kwargs):
        super(DebugModeInterface, self).__init__(**kwargs)
        self.debug_mode = DebugMode()

    def open_user_creation(self):
        popup = UserCreationInterface(self)
        popup.open()

    def open_user_management(self):
        popup = UserManagementInterface(self)
        popup.ready()
        popup.open()

    def create_user(self, username, character, location, sublocation, position):
        self.debug_mode.create_user(username, character, location, sublocation, position)

    def send_message(self, username, message, sprite_name, delay_in_s):
        self.debug_mode.send_message(username, message, sprite_name, delay_in_s)


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
        main_screen = App.get_running_app().get_main_screen()
        main_screen.users[username] = user
        main_screen.ooc_window.add_user(user)

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

    def send_message(self, username, message, sprite_name, delay_in_s):
        user = self.created_users[username]
        if sprite_name == '':
            sprite_name = self.get_random_sprite(user)
        user.set_current_sprite(sprite_name)
        Clock.schedule_once(partial(self.scheduled_send_message, user, message), int(delay_in_s))

    def get_random_sprite(self, user):
        icons = user.character.icons.textures
        sprite_name = choice(list(icons.keys()))
        return sprite_name

    def scheduled_send_message(self, user, message, dt):
        username = user.username
        loc = user.get_loc().name
        subloc = user.get_subloc().name
        char = user.character.name
        sprite = user.current_sprite
        pos = user.pos
        col_id = "0"
        sprite_option = "-1"
        connection_manager = App.get_running_app().get_user_handler().get_connection_manager()
        message_factory = App.get_running_app().get_message_factory()
        message = message_factory.build_chat_message(content=message, location=loc, sublocation=subloc,
                                                     character=char, sprite=sprite,
                                                     position=pos, color_id=col_id,
                                                     sprite_option=sprite_option, username=username)
        connection_manager.send_local(message)

    def get_created_users(self):
        return self.created_users
