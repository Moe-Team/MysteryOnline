import configparser
import re

from MysteryOnline import get_version, get_dev
from MysteryOnline.character import characters
from MysteryOnline.character_select import CharacterSelect
from MysteryOnline.irc_mo import IrcConnection, ConnectionManager
from kivy.app import App
from kivy.clock import Clock
from kivy.config import ConfigParser
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import Screen
from MysteryOnline.mopopup import MOPopup, MOPopupFile, FormPopup
from MysteryOnline.user import User, CurrentUserHandler

dirty = False
config = configparser.ConfigParser()
config.read('irc_channel_name.ini')

if not config.has_section("Channel name"):
    config.add_section("Channel name")
    dirty = True

if not config.has_option("Channel name", "channel"):
    config.set("Channel name", "channel", "#mysteryonline")
    dirty = True

channel_in_config = config.get("Channel name", "channel")

if not config.has_option("Channel name", "password"):
    config.set("Channel name", "password", "")
    dirty = True

password_in_config = config.get("Channel name", "password")

if not config.has_section("IRC Server name"):
    config.add_section("IRC Server name")
    dirty = True

if not config.has_option("IRC Server name", "irc_server"):
    config.set("IRC Server name", "irc_server", "irc.zumorica.es")
    dirty = True

irc_server = config.get("IRC Server name", "irc_server")

if not config.has_option("IRC Server name", "irc_server_port"):
    config.set("IRC Server name", "irc_server_port", "6665")
    dirty = True

irc_server_port = config.get("IRC Server name", "irc_server_port")

if dirty:
    with open('irc_channel_name.ini', "w+") as configfile:
        config.write(configfile)

SERVER = irc_server
PORT = int(irc_server_port)
'''The PORT variable needs an integer to work so we convert the irc_server_port variable into an integer
 and that does the job.'''
CHANNEL = channel_in_config
PASSWORD = password_in_config


class LoginScreen(Screen):
    username = StringProperty('')
    version_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.picked_char = None
        self.server = SERVER
        self.port = PORT
        self.channel = CHANNEL
        self.password = PASSWORD
        if get_dev():
            Clock.schedule_once(self.on_login_clicked, 0)
        Clock.schedule_once(self.set_version_label, 0)

    def set_version_label(self, *args):
        self.version_label.text = get_version()

    def on_login_clicked(self, *args):
        if self.username == '' or not self.is_username_valid():
            popup = MOPopup("Error", "Invalid username", "Whatever you say, mate")
            popup.open()
            return
        if len(self.username) > 16:
            MOPopup("Error", "Username too long (max 16 characters)", "Oh, okay").open()
            return
        self.set_username_as_last_used()
        self.set_current_user()
        self.create_irc_connection()

    def create_irc_connection(self):
        user_handler = App.get_running_app().get_user_handler()
        connection = IrcConnection(self.server, self.port, self.channel, self.username, self.password)
        user_handler.set_connection_manager(ConnectionManager(connection))
        self.manager.irc_connection = connection

    def set_current_user(self):
        config = ConfigParser()
        config.read('mysteryonline.ini')
        user = User(self.username)
        user_handler = CurrentUserHandler(user)
        if self.picked_char is not None:
            user.set_char(self.picked_char)
            user.get_char().load()
        else:
            try:
                user.set_char(characters[str(config.get('other', 'last_character'))])
                user.get_char().load()
            except KeyError:
                red_herring = characters['RedHerring']
                user.set_char(red_herring)
                user.get_char().load()
            except configparser.NoSectionError:
                App.get_running_app().build_config(config)
                config.write()
        App.get_running_app().set_user(user)
        App.get_running_app().set_user_handler(user_handler)

    def set_username_as_last_used(self):
        main_config = App.get_running_app().config
        main_config.set('other', 'last_username', self.username)

    # noinspection PyTypeChecker
    def is_username_valid(self):
        p = re.compile(r"[a-z_\d][a-z_\d-]+", re.I)
        if not re.fullmatch(p, self.username):
            return False
        return True

    def on_select_clicked(self, *args):
        cs = CharacterSelect()
        cs.bind(on_dismiss=self.on_picked)
        cs.open()

    def on_server_clicked(self, *args):
        def on_popup_validate(fields={}):
            if not fields["channel"].text.startswith("#"):
                return False

            try:
                int(fields["IRC Server Port"].text)
            except ValueError:
                return False

            return True

        def on_popup_submitted(popup, fields={}):
            config.set("Channel name", "channel", fields["channel"].text)
            config.set("Channel name", "password", fields["password"].text)
            config.set("IRC Server name", "irc_server", fields["IRC Server"].text)
            config.set("IRC Server name", "irc_server_port", fields["IRC Server Port"].text)

            with open('irc_channel_name.ini', "w+") as configfile:
                config.write(configfile)

            self.channel = fields["channel"].text
            self.password = fields["password"].text
            self.server = fields["IRC Server"].text
            self.port = int(fields["IRC Server Port"].text)

        def on_popup_error(popup, fields={}):
            epopup = MOPopup("Something went wrong", "You entered invalid data.", "Aw, shucks.")
            epopup.open()

        popup = FormPopup("Server selection", on_popup_validate, on_popup_submitted, on_popup_error, submit_text="Save", size_hint= [0.5, 0.9])
        popup.add_field("channel", True, text=self.channel)
        popup.add_field("password", False, text=self.password)
        popup.add_field("IRC Server", True, text=self.server)
        popup.add_field("IRC Server Port", True, text=str(self.port))
        popup.open()

    def on_picked(self, inst):
        self.picked_char = inst.picked_char

    def on_help_clicked(self, *args):
        popup = MOPopupFile('Help', 'help.txt')
        popup.open()

    def on_rules_clicked(self, *args):
        popup = MOPopupFile('Rules', 'rules.txt')
        popup.open()
