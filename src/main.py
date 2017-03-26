from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty
from kivy.clock import Clock

from loginscreen import LoginScreen
from mainscreen import MainScreen
from settingsscreen import SettingsScreen


class MainScreenManager(ScreenManager):
    irc_connection = ObjectProperty(None)

    def on_irc_connection(self, *args):
        Clock.schedule_interval(self.process_irc, 1.0/60.0)
        self.current = "main"

    def process_irc(self, dt):
        self.irc_connection.process()


class MysteryOnlineApp(App):

    def build(self):
        msm = MainScreenManager()
        return msm


if __name__ == "__main__":
    MysteryOnlineApp().run()
