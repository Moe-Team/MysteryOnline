from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.properties import StringProperty
from mopopup import MOPopup, MOPopupFile
from character_select import CharacterSelect
from character import characters
import re
from kivy.config import ConfigParser
from irc_mo import IrcConnection, ConnectionManager
from user import User, CurrentUserHandler

import configparser

config = configparser.ConfigParser()
config.read('irc_channel_name.ini')
try:
    channel_in_config = config.get("Channel name", 'Channel')
    irc_server = config.get("IRC Server name", 'irc_server')
    irc_server_port = config.get("IRC Server name", 'irc_server_port')
except configparser.NoSectionError:
    config.read('irc_channel_name.ini')
    if not config.has_section('Channel name'):
        config.add_section('Channel name')
        config.set('Channel name', 'Channel', '##mysteryonlinetest')
    if not config.has_section('IRC Server name'):
        config.add_section('IRC Server name')
        config.set('IRC Server name', 'irc_server', 'chat.freenode.net')
        config.set('IRC Server name', 'irc_server_port', '6665')
    channel_in_config = config.get("Channel name", 'Channel')
    irc_server = config.get("IRC Server name", 'irc_server')
    irc_server_port = config.get("IRC Server name", 'irc_server_port')
    with open('irc_channel_name.ini', "w+") as configfile:
        config.write(configfile)

SERVER = irc_server
PORT = int(irc_server_port)
'''The PORT variable needs an integer to work so we convert the irc_server_port variable into an integer
 and that does the job.'''
CHANNEL = channel_in_config


class LoginScreen(Screen):
    username = StringProperty('')

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.picked_char = None

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
        connection = IrcConnection(SERVER, PORT, CHANNEL, self.username)
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

    def on_picked(self, inst):
        self.picked_char = inst.picked_char

    def on_help_clicked(self, *args):
        popup = MOPopupFile('Help', 'help.txt')
        popup.open()

    def on_rules_clicked(self, *args):
        popup = MOPopupFile('Rules', 'rules.txt')
        popup.open()
