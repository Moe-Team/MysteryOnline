from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import re

from irc_mo import IrcConnection

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
                popup = Popup(title="Error", content=Label(text="Invalid username"),
                size_hint=(None, None), size=(400, 400))
                popup.open()
                return
            self.manager.irc_connection = IrcConnection(SERVER, PORT, CHANNEL, self.username)
