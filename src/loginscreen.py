from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
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
                popup_content = BoxLayout(orientation='vertical')
                popup_content.add_widget(Label(text="Invalid username"))
                btn = Button(text="Whatever you say, mate", size_hint=(1, 0.4))
                popup_content.add_widget(btn)
                popup = Popup(title="Error", content=popup_content,
                size_hint=(None, None), size=(400, 200))
                popup.open()
                btn.bind(on_press=popup.dismiss)
                return

            self.manager.irc_connection = IrcConnection(SERVER, PORT, CHANNEL, self.username)
