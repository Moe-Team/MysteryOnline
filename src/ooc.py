import threading
from datetime import datetime

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.utils import escape_markup
from kivy.logger import Logger

from private_message_screen import PrivateMessageScreen
from user_box import UserBox


class OOCLogLabel(Label):
    def __init__(self, **kwargs):
        super(OOCLogLabel, self).__init__(**kwargs)


class MusicTab(TabbedPanelItem):
    url_input = ObjectProperty(None)
    loop_checkbox = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MusicTab, self).__init__(**kwargs)
        self.track = None
        self.loop = True

    def on_music_play(self, url=None):
        if url is None:
            url = self.url_input.text
            self.url_input.text = ""
            connection_manager = App.get_running_app().get_user_handler().get_connection_manager()
            connection_manager.update_music(url)
            main_screen = App.get_running_app().get_main_screen()
            main_screen.log_window.log.text += "You changed the music.\n"
            config = App.get_running_app().config
            if config.getdefaultint('other', 'log_scrolling', 1):
                main_screen.log_window.log.scroll_y = 0
        if not any(s in url.lower() for s in ('mp3', 'wav', 'ogg', 'flac')):
            Logger.warning("Music: The file you tried to play doesn't appear to contain music.")
            return

        def play_song(root):
            track = root.track
            if track is not None and track.state == 'play':
                track.stop()
            try:
                r = requests.get(url)
            except requests.exceptions.MissingSchema:
                Logger.warning('Music: Invalid URL')
                return
            f = open("temp.mp3", mode="wb")
            f.write(r.content)
            f.close()
            track = SoundLoader.load("temp.mp3")
            config_ = App.get_running_app().config
            track.volume = config_.getdefaultint('sound', 'music_volume', 100) / 100
            track.loop = root.loop
            track.play()
            root.track = track

        threading.Thread(target=play_song, args=(self,)).start()

    def music_stop(self, local=True):
        if self.track is not None:
            if self.track.state == 'play':
                self.track.stop()
                main_screen = self.parent.parent
                if local:
                    main_screen.update_music("stop")
                    main_screen.log_window.log.text += "You stopped the music.\n"
                    config = App.get_running_app().config
                    if config.getdefaultint('other', 'log_scrolling', 1):
                        main_screen.log_window.log.scroll_y = 0

    def on_loop(self, c, value):
        self.loop = value

    def reset_music(self, *args):
        if self.track is not None:
            self.track.stop()


class OOCWindow(TabbedPanel):
    user_list = ObjectProperty(None)
    ooc_chat_header = ObjectProperty(None)
    ooc_input = ObjectProperty(None)
    blip_slider = ObjectProperty(None)
    music_slider = ObjectProperty(None)
    music_tab = ObjectProperty(None)
    effect_slider = ObjectProperty(None)
    chat_grid = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(OOCWindow, self).__init__(**kwargs)
        self.online_users = {}
        self.ooc_notif = SoundLoader.load('sounds/general/notification.mp3')
        self.pm_notif = SoundLoader.load('sounds/general/codeccall.wav')
        self.pm_open_sound = SoundLoader.load('sounds/general/codecopen.wav')
        self.ooc_play = True
        self.chat = PrivateMessageScreen()
        self.muted_users = []
        self.pm_buttons = []
        self.pm_flag = False
        self.pm_window_open_flag = False
        self.ooc_chat = OOCLogLabel()
        self.counter = 0

    def ready(self, main_scr):
        self.ooc_chat.bind(on_ref_press=main_scr.log_window.copy_text)
        self.add_user(main_scr.user)
        self.chat_grid.bind(minimum_height=self.chat_grid.setter('height'))
        self.ooc_chat.bind(on_ref_press=main_scr.log_window.copy_text)
        self.chat_grid.add_widget(self.ooc_chat)
        config = App.get_running_app().config  # The main config
        config.add_callback(self.on_blip_volume_change, 'sound', 'blip_volume')
        self.blip_slider.value = config.getdefaultint('sound', 'blip_volume', 100)
        config.add_callback(self.on_music_volume_change, 'sound', 'music_volume')
        self.music_slider.value = config.getdefaultint('sound', 'music_volume', 100)
        config.add_callback(self.on_ooc_volume_change, 'sound', 'effect_volume')
        self.effect_slider.value = config.getdefaultint('sound', 'effect_volume', 100)
        self.ooc_chat_header.bind(on_press=self.on_ooc_checked)
        self.chat.ready()
        if self.chat.irc is None:
            self.chat.irc = self.parent.parent.manager.irc_connection
        self.chat.username = self.parent.parent.user.username
        Clock.schedule_interval(self.update_private_messages, 1.0 / 60.0)
        v = config.getdefaultint('sound', 'effect_volume', 100)
        self.ooc_notif.volume = v / 100
        self.pm_notif.volume = v / 100
        self.pm_open_sound.volume = v / 100

    def on_blip_volume_change(self, s, k, v):
        self.blip_slider.value = v

    def on_slider_blip_value(self, *args):
        config = App.get_running_app().config
        value = int(self.blip_slider.value)
        config.set('sound', 'blip_volume', value)

    def on_music_volume_change(self, s, k, v):
        self.music_slider.value = v

    def on_slider_music_value(self, *args):
        config = App.get_running_app().config
        value = int(self.music_slider.value)
        if self.music_tab.track is not None:
            self.music_tab.track.volume = value / 100
        config.set('sound', 'music_volume', value)

    def on_ooc_volume_change(self, s, k, v):
        self.effect_slider.value = v
        self.ooc_notif.volume = int(v) / 100
        self.pm_notif.volume = int(v) / 100
        self.pm_open_sound.volume = int(v) / 100

    def on_slider_effect_value(self, *args):
        config = App.get_running_app().config
        value = int(self.effect_slider.value)
        config.set('sound', 'effect_volume', value)

    def add_user(self, user):
        char = user.get_char()
        main_screen = self.parent.parent
        if char is None:
            char = ""
        else:
            char = char.name
        if user.username not in (main_screen.user.username, '@ChanServ', 'ChanServ'):
            user_box = UserBox(size_hint_y=None, height=40)
            user_box.lbl.text = "{}: {}\n".format(user.username, char)
            user_box.pm.bind(on_press=lambda x: self.open_private_msg_screen(user.username, user_box.pm))
            self.pm_buttons.append(user_box.pm)
            user_box.mute.bind(on_press=lambda x: self.mute_user(user, user_box.mute))
            self.user_list.add_widget(user_box)
            self.online_users[user.username] = user_box

    def update_char(self, username, char):
        user_box = self.online_users.get(username, None)
        if user_box is None:
            return
        user_box.set_char_label(char)

    def update_loc(self, username, loc):
        user_box = self.online_users.get(username, None)
        if user_box is None:
            return
        user_box.set_loc_label(loc)

    def update_subloc(self, username, subloc):
        user_box = self.online_users.get(username, None)
        if user_box is None:
            return
        user_box.set_sub_label(subloc)

    def open_private_msg_screen(self, username, pm):  # Opens the PM window
        self.pm_window_open_flag = True
        pm.background_color = (1, 1, 1, 1)
        self.chat.build_conversation(username)
        self.chat.set_current_conversation_user(username)
        self.chat.open()
        self.pm_open_sound.play()

    def muted_sender(self, pm, muted_users):  # Checks whether the sender of a pm is muted
        for x in range(len(muted_users)):
            if pm.sender == muted_users[x].username:
                return True
        return False

    def update_private_messages(self, *args):  # Acts on arrival of PMs
        main_scr = self.parent.parent
        irc = main_scr.manager.irc_connection
        pm = irc.get_pm()
        if pm is not None:
            if pm.sender != self.chat.username:
                if not self.muted_sender(pm, self.muted_users):
                    if not self.pm_window_open_flag:
                        for x in range(len(self.online_users)):
                            if pm.sender == self.pm_buttons[x].id:
                                self.pm_buttons[x].background_color = (1, 0, 0, 1)
                                break
                        if not self.pm_flag:
                            self.pm_notif.play()
                    self.pm_flag = True
                    self.chat.build_conversation(pm.sender)
                    self.chat.set_current_conversation_user(pm.sender)
                    self.chat.update_conversation(pm.sender, pm.msg)

    def mute_user(self, user, btn):
        if user in self.muted_users:
            self.muted_users.remove(user)
            btn.text = 'Mute'
        else:
            self.muted_users.append(user)
            btn.text = 'Unmute'

    def delete_user(self, username):
        try:
            label = self.online_users[username]
        except KeyError:
            return
        self.user_list.remove_widget(label)
        del self.online_users[username]

    def on_ooc_checked(self, *args):
        self.ooc_chat_header.background_normal = 'atlas://data/images/defaulttheme/button'
        self.ooc_chat_header.background_color = [1, 1, 1, 1]

    def update_ooc(self, msg, sender):
        ref = msg
        if sender == 'default':
            sender = App.get_running_app().get_user().username
        if 'www.' in msg or 'http://' in msg or 'https://' in msg:
            msg = "[u]{}[/u]".format(msg)
        if self.counter == 100:
            self.counter = 0
            self.ooc_chat = OOCLogLabel()
            self.chat_grid.add_widget(self.ooc_chat)
            main_scr = self.parent.parent
            self.ooc_chat.bind(on_ref_press=main_scr.log_window.copy_text)
        self.ooc_chat.text += "{0}: [ref={2}]{1}[/ref]\n".format(sender, msg, escape_markup(ref))
        self.counter += 1
        config = App.get_running_app().config
        if config.getdefaultint('other', 'ooc_scrolling', 1):
            self.ooc_chat.parent.parent.scroll_y = 0
        now = datetime.now()
        cur_date = now.strftime("%d-%m-%Y")
        cur_time = now.strftime("%H:%M:%S")
        log_msg = "<{} {}> {}: {}\n".format(cur_time, cur_date, sender, msg)
        with open('ooc_log.txt', 'a', encoding='utf-8') as f:
            f.write(log_msg)
        if self.current_tab != self.ooc_chat_header:
            color = [0, 0.5, 1, 1]
            if self.ooc_chat_header.background_color != color:
                self.ooc_chat_header.background_normal = ''
                self.ooc_chat_header.background_color = color
            if self.ooc_play:
                self.ooc_notif.play()
                config = App.get_running_app().config
                delay = config.getdefaultint('other', 'ooc_notif_delay', 60)
                Clock.schedule_once(self.ooc_time_callback, delay)
                self.ooc_play = False

    def ooc_time_callback(self, *args):
        self.ooc_play = True

    def send_ooc(self):
        Clock.schedule_once(self.refocus_text)
        msg = self.ooc_input.text
        main_scr = self.parent.parent
        irc = main_scr.manager.irc_connection
        irc.send_special('OOC', msg)
        self.ooc_input.text = ""

    def refocus_text(self, *args):
        self.ooc_input.focus = True
