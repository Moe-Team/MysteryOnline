from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from loginscreen import LoginScreen
from mainscreen import MainScreen
from settingsscreen import SettingsScreen


class MainScreenManager(ScreenManager):
    pass


class MysteryOnlineApp(App):

    def build(self):
        msm = MainScreenManager()
        msm.add_widget(LoginScreen(name="login"))
        msm.add_widget(MainScreen(name="main"))
        msm.add_widget(SettingsScreen(name="settings"))
        return msm


if __name__ == "__main__":
    MysteryOnlineApp().run()
