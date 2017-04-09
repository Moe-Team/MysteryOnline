from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.properties import StringProperty, ObjectProperty
from mopopup import MOPopup

import re

from irc_mo import IrcConnection
from user import User

SERVER = "chat.freenode.net"
PORT = 6665
CHANNEL = "##mysteryonline"

class LoginScreen(Screen):
    username = StringProperty('')

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

    def on_login_clicked(self, *args):
            p = re.compile(r"[a-z_\d][a-z_\d-]+", re.I)
            if not re.fullmatch(p, self.username):
                popup = MOPopup("Error", "Invalid username", "Whatever you say, mate")
                popup.open()
                return

            self.manager.irc_connection = IrcConnection(SERVER, PORT, CHANNEL, self.username)
            App.get_running_app().set_user(User(self.username))
