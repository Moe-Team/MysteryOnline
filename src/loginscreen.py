from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.label import Label

from irc_mo import IrcConnection

SERVER = "chat.freenode.net"
PORT = 6665
CHANNEL = "##mysteryonline"

class LoginScreen(Screen):
    username = StringProperty('')

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

    def on_login_clicked(self, *args):
            self.manager.irc_connection = IrcConnection(SERVER, PORT, CHANNEL, self.username)
