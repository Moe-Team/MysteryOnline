from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.config import Config

from loginscreen import LoginScreen
from mainscreen import MainScreen
from settingsscreen import SettingsScreen
from mopopup import MOPopup
from location import locations

Config.set('kivy', 'desktop', '1')
Config.set('input', 'mouse', 'mouse,disable_multitouch')


class MainScreenManager(ScreenManager):
    main_screen = ObjectProperty(None)
    irc_connection = ObjectProperty(None)
    connected = BooleanProperty(False)

    def on_irc_connection(self, *args):
        self.irc_connection.on_join_handler = self.main_screen.on_join
        self.irc_connection.on_users_handler = self.main_screen.on_join_users
        self.irc_connection.on_disconnect_handler = self.main_screen.on_disconnect
        self.main_screen.user = App.get_running_app().get_user()
        Clock.schedule_interval(self.process_irc, 1.0/60.0)
        self.popup_ = MOPopup("Connection", "Connecting to IRC", "K", False)
        self.popup_.open()

    def on_connected(self, *args):
        self.popup_.dismiss()
        del self.popup_
        self.current = "main"
        self.main_screen.on_ready()
        Clock.schedule_interval(self.main_screen.update_chat, 1.0/60.0)

    def process_irc(self, dt):
        self.irc_connection.process()
        self.connected = self.irc_connection.is_connected()


class MysteryOnlineApp(App):

    def build(self):
        msm = MainScreenManager()
        locations['Hakuryou'].load()
        return msm

    def set_user(self, user):
        self.user = user

    def get_user(self):
        return self.user

    def set_main_screen(self, scr):
        self.main_screen = scr

    def get_main_screen(self):
        return self.main_screen


if __name__ == "__main__":
    MysteryOnlineApp().run()
