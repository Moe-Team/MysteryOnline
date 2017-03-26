from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.clock import Clock

from loginscreen import LoginScreen
from mainscreen import MainScreen
from settingsscreen import SettingsScreen


class MainScreenManager(ScreenManager):
    main_screen = ObjectProperty(None)
    irc_connection = ObjectProperty(None)
    connected = BooleanProperty(False)

    def on_irc_connection(self, *args):
        Clock.schedule_interval(self.process_irc, 1.0/60.0)

    def on_connected(self, *args):
        self.current = "main"
        Clock.schedule_interval(self.main_screen.update_chat, 1.0/60.0)

    def process_irc(self, dt):
        self.irc_connection.process()
        self.connected = self.irc_connection.is_connected()


class MysteryOnlineApp(App):

    def build(self):
        msm = MainScreenManager()
        return msm


if __name__ == "__main__":
    MysteryOnlineApp().run()
