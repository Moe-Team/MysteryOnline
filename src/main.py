# import os
#
# wrong_path = os.environ['GST_PLUGIN_PATH']
# right_path = os.getcwd()
# pattern = '{}:'.format(right_path)
# to_replace = '{};'.format(right_path)
#
# fixed_path = wrong_path.replace(pattern, to_replace)
# os.environ['GST_PLUGIN_PATH'] = fixed_path


import set_kivy_config
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.clock import Clock

from loginscreen import LoginScreen
from mainscreen import MainScreen

from mopopup import MOPopup
from location import locations


class MainScreenManager(ScreenManager):
    main_screen = ObjectProperty(None)
    irc_connection = ObjectProperty(None)
    connected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(MainScreenManager, self).__init__(**kwargs)
        self.popup_ = MOPopup("Connection", "Connecting to IRC", "K", False)

    def on_irc_connection(self, *args):
        """Called when the IRC connection is created"""

        self.set_handlers()
        self.main_screen.user = App.get_running_app().get_user()
        Clock.schedule_interval(self.process_irc, 1.0/60.0)
        self.popup_.open()

    def set_handlers(self):
        connection_manager = App.get_running_app().get_user_handler().get_connection_manager()
        self.irc_connection.on_join_handler = connection_manager.on_join
        self.irc_connection.on_users_handler = connection_manager.on_join_users
        self.irc_connection.on_disconnect_handler = connection_manager.on_disconnect

    def on_connected(self, *args):
        """Called when MO connects to the IRC channel"""

        self.unset_the_r_flag()
        self.popup_.dismiss()
        del self.popup_
        self.current = "main"
        self.main_screen.on_ready()
        connection_manager = App.get_running_app().get_user_handler().get_connection_manager()
        Clock.schedule_interval(connection_manager.update_chat, 1.0/60.0)

    def unset_the_r_flag(self):
        """Fixes being unable to receive private messages from other users"""

        username = App.get_running_app().get_user().username
        self.irc_connection.send_mode(username, "-R")

    def process_irc(self, dt):
        self.irc_connection.process()
        self.connected = self.irc_connection.is_connected()


class MysteryOnlineApp(App):
    use_kivy_settings = False

    def __init__(self, **kwargs):
        super(MysteryOnlineApp, self).__init__(**kwargs)
        self.user = None
        self.main_screen = None
        self.user_handler = None

    def build(self):
        msm = MainScreenManager()
        for l in locations:
            locations[l].load()
        return msm

    def build_config(self, config):
        config.setdefaults('display', {
            'resolution': '1920x1080',
        })
        config.setdefaults('sound', {
            'blip_volume': 100,
            'music_volume': 100,
            'effect_volume': 100
        })
        config.setdefaults('other', {
            'ooc_notif_delay': 60,
            'log_scrolling': 1,
            'ooc_scrolling': 1,
            'last_username': 'YourUsernameHere',
            'textbox_speed': 60,
            'textbox_transparency': 60
        })

    def build_settings(self, settings):
        settings.add_json_panel('Display', self.config, 'settings.json')
        settings.add_json_panel('Sound', self.config, 'settings2.json')
        settings.add_json_panel('Other', self.config, 'settings3.json')

    def set_user(self, user):
        self.user = user

    def get_user(self):
        return self.user

    def set_main_screen(self, scr):
        self.main_screen = scr

    def get_main_screen(self):
        return self.main_screen

    def set_user_handler(self, user_handler):
        self.user_handler = user_handler

    def get_user_handler(self):
        return self.user_handler

    def on_stop(self):
        if self.main_screen:
            self.main_screen.on_stop()
        self.config.write()
        super(MysteryOnlineApp, self).on_stop()


if __name__ == "__main__":
    MysteryOnlineApp().run()


__all__ = ['set_kivy_config', 'LoginScreen', 'MainScreen']
