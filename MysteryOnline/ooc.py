import threading
import traceback
import tempfile
import weakref
from datetime import datetime

import requests
import urllib
from irc.client import MessageTooLong
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.utils import escape_markup
from kivy.logger import Logger
from kivy.utils import platform

from MysteryOnline.mopopup import MOPopup
from MysteryOnline.private_message_screen import PrivateMessageScreen
from MysteryOnline.user_box import UserBox
from requests.exceptions import Timeout, MissingSchema
from MysteryOnline.mopopup import MOPopup

import json
import youtube_dl
import os
import shutil

from MysteryOnline.user import CurrentUserHandler

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': False,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'writeinfojson': True
}


# this thing lets you declare what shit you want ur download to be, neat!!

class OOCLogLabel(Label):
    def __init__(self, **kwargs):
        super(OOCLogLabel, self).__init__(**kwargs)


class MusicTab(TabbedPanelItem):
    url_input = ObjectProperty(None)
    loop_checkbox = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MusicTab, self).__init__(**kwargs)
        self.track = None
        self.tracks = []
        self.loop = True
        self.download = True
        self.hide_title = False
        self.is_loading_music = False
        self.all_track_stop_lock = threading.Lock()

    def on_music_play(self, sender='Default', url=None, send_to_all=True, track_name=None):
        if "dropbox" in self.url_input.text:
            self.url_input.text = self.url_input.text.replace(self.url_input.text[len(self.url_input.text) - 1], '1')
        if self.is_loading_music or not self.download:
            return
        self.is_loading_music = True
        main_screen = App.get_running_app().get_main_screen()
        # TODO : Variable user not being used, need to give it a purpose?
        user = App.get_running_app().get_user()
        if self.hide_title and sender == 'Default':
            track_name = "Hidden track"
        if url is None:
            if len(self.url_input.text) > 400:
                popup = MOPopup("Warning", "URL too long", "OK")
                popup.open()
                return
            url = self.url_input.text
        if track_name is not None:
            main_screen.music_name_display.text = "Playing: {}".format(track_name)
        else:
            main_screen.music_name_display.text = "Playing: URL Track"
        try:
            if send_to_all:
                self.url_input.text = ""
                connection_manager = App.get_running_app().get_user_handler().get_connection_manager()
                connection_manager.update_music(track_name, url)
                main_screen.log_window.add_entry("You changed the music.\n")
            if not any(s in url.lower() for s in ('mp3', 'wav', 'ogg', 'flac', 'watch')):  # watch is for yt links
                Logger.warning("Music: The file you tried to play doesn't appear to contain music.")
                self.is_loading_music = False
                return
        except MessageTooLong:
            self.url_input.text = ""
            temp_pop = MOPopup("Error playing music", "Link too long", "OK")
            temp_pop.open()

        def play_song(root):
            config_ = App.get_running_app().config
            music_path = "mucache"
            temp_dir = None

            if not config_.getboolean('sound', 'musiccache'):
                temp_dir: tempfile.TemporaryDirectory = tempfile.TemporaryDirectory()
                music_path = temp_dir.name
            else:
                try:  # kebab
                    os.makedirs('mucache')
                except FileExistsError:
                    pass
            main_scr = App.get_running_app().get_main_screen()
            root.is_loading_music = True
            root.stop_all_tracks()
            if url.find("youtube") == -1:  # checks if youtube is not in url string
                try:  # does the normal stuff
                    r = requests.get(url, timeout=(5, 20))
                    """If no request were established within 5 seconds, it will raise a Timeout exception.
                       If no data was received within 20 seconds, it will also raise the same exception."""
                    r.raise_for_status()
                    """ Any HTTP Error that's between 400 and 600 will force the HTTPError exception to be raised.
                        root.is_loading_music was moved to be more global inside the method because if a http error is 
                        raised, the value of the variable won't be changed when it should be set to false. It also
                        removes the need to have to set it to false within each exception block."""
                except MissingSchema:
                    Logger.warning('Music Error: Invalid URL. Did you forget to add http:// at the beginning '
                                   'by any chance?')
                    main_scr.music_name_display.text = "Error: Invalid URL. See warning logs for more details."
                    return
                except Timeout:
                    Logger.warning('Music Error: Request timed out. Either the server is not responding back or you '
                                   'lost connection to internet.')
                    main_scr.music_name_display.text = "Error: Request timed out. See warning logs for more details."
                    return
                if r.ok:  # no errors were raised, it's now loading the music.
                    '''write a function for this?'''
                    songtitle = urllib.request.urlopen(urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})).info().get_filename()
                    if songtitle is None:
                        songtitle = "temp"
                    elif track_name != None:
                        songtitle = track_name
                    else:
                        songtitle = os.path.basename(songtitle)
                        songtitle = os.path.splitext(songtitle)[0]  # safer way to get the song title
                        songtitle = songtitle.encode('latin-1').decode('utf-8') #nonascii names break otherwise, go figure
                    root.is_loading_music = True

                file = os.path.join(music_path, songtitle+'.mp3')
                if not os.path.isfile(file):
                    try:
                        f = open(file, mode="wb")
                    except OSError:
                        songtitle = 'Error Name'
                        f = open(file, mode="wb")
                    f.write(r.content)
                    f.close()
            else:
                try:
                    ytdl_format_options['outtmpl'] = os.path.join(music_path, "%(title)s.mp3")
                    with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:  # the actual downloading
                        info = ydl.extract_info(url, download=False)
                        songtitle = ydl.prepare_filename(info)
                        songtitle = os.path.basename(songtitle)
                        songtitle = os.path.splitext(songtitle)[0] #safer way to get the song title
                        if not os.path.isfile(os.path.join(music_path, songtitle+'.mp3')):
                            ydl.download([url])
                except Exception as e:
                    Logger.warning(traceback.format_exc())
                    if e is AttributeError:
                        main_scr.music_name_display.text = "Error: bad url"
                    else:
                        main_scr.music_name_display.text = "Error"
                    root.is_loading_music = False
                    return
            track = SoundLoader.load(os.path.join(music_path, songtitle+".mp3"))
            track.loop = root.loop
            track.volume = App.get_running_app().exponential_volume(config_.getdefaultint('sound', 'music_volume', 100.0))
            root.track = track
            track.play()
            root.tracks.append(weakref.ref(track))
            root.is_loading_music = False
            if track_name != "Hidden track":
                if 'youtube' in url:
                    with open(os.path.join(music_path, songtitle+'.mp3.info.json'), 'r') as f:
                        video_info = json.load(f)
                    main_scr.music_name_display.text = "Playing: {}".format(video_info['fulltitle'])
                else:
                    main_scr.music_name_display.text = "Playing: " + songtitle

        threading.Thread(target=play_song, args=(self,), daemon=True).start()

    def music_stop(self, local=True):
        if self.track is not None:
            if self.track.state == 'play':
                self.track.stop()
                main_screen = App.get_running_app().get_main_screen()
                main_screen.music_name_display.text = "Playing: "
                if local:
                    connection = App.get_running_app().get_user_handler().get_connection_manager()
                    connection.update_music("stop")
                    main_screen.log_window.add_entry("You stopped the music.\n")

    def stop_all_tracks(self):
        with self.all_track_stop_lock:
            for ref in self.tracks:
                track = ref()
                if track is None:
                    self.tracks.remove(ref)
                    continue
                if track.state == "play":
                    track.stop()
                if platform != "win":
                    track.unload()
            self.tracks.clear()
            self.track = None

    def on_loop(self, value):
        self.loop = value

    def on_hide(self, value):
        self.hide_title = value

    def on_download(self, value):
        self.download = value

    def reset_music(self, *args):
        self.is_loading_music = False
        main_screen = App.get_running_app().get_main_screen()
        main_screen.music_name_display.text = "Playing: "
        self.stop_all_tracks()


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
        if platform != "win":
            self.ooc_notif.unload()
        self.pm_notif_volume = 0
        self.pm_open_sound_volume = 0
        self.ooc_play = True
        self.chat = PrivateMessageScreen()
        self.muted_users = []
        self.pm_buttons = []
        self.ooc_chat = OOCLogLabel()
        self.counter = 0

    def ready(self, main_scr):
        self.ooc_chat.bind(on_ref_press=main_scr.log_window.copy_text)
        self.add_user(main_scr.user)
        self.chat_grid.bind(minimum_height=self.chat_grid.setter('height'))
        self.ooc_chat.bind(on_ref_press=main_scr.log_window.copy_text)
        self.chat_grid.add_widget(self.ooc_chat)
        config = App.get_running_app().config  # The main config
        v = config.getdefaultint('sound', 'effect_volume', 100)
        config.add_callback(self.on_blip_volume_change, 'sound', 'blip_volume')
        self.blip_slider.value = config.getdefaultint('sound', 'blip_volume', 100)
        config.add_callback(self.on_music_volume_change, 'sound', 'music_volume')
        self.music_slider.value = config.getdefaultint('sound', 'music_volume', 100)
        config.add_callback(self.on_ooc_volume_change, 'sound', 'effect_volume')
        self.effect_slider.value = v
        try:
            self.ooc_notif.volume = App.get_running_app().exponential_volume(v)
            self.pm_notif_volume = App.get_running_app().exponential_volume(v)
            self.pm_open_sound_volume = App.get_running_app().exponential_volume(v)
        except AttributeError:
            pass
        self.ooc_chat_header.bind(on_press=self.on_ooc_checked)
        self.chat.ready()
        main_scr = App.get_running_app().get_main_screen()
        if self.chat.irc is None:
            self.chat.irc = main_scr.manager.irc_connection
        self.chat.username = main_scr.user.username
        Clock.schedule_interval(self.update_private_messages, 1.0 / 60.0)
        self.user_list.bind(minimum_height=self.user_list.setter('height'))

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
        try:
            self.music_tab.track.volume = App.get_running_app().exponential_volume(value)
        except AttributeError:
            pass

        config.set('sound', 'music_volume', value)

    def on_ooc_volume_change(self, s, k, v):
        self.effect_slider.value = v

    def on_slider_effect_value(self, *args):
        config = App.get_running_app().config
        value = int(self.effect_slider.value)
        try:
            self.ooc_notif.volume = App.get_running_app().exponential_volume(value)
            self.pm_notif_volume = App.get_running_app().exponential_volume(value)
            self.pm_open_sound_volume = App.get_running_app().exponential_volume(value)
        except AttributeError:
            pass
        config.set('sound', 'effect_volume', value)

    def add_user(self, user):
        char = user.get_char()
        main_screen = App.get_running_app().get_main_screen()
        if char is None:
            char = ""
        else:
            char = char.name
        if user.username not in (main_screen.user.username, '@ChanServ', 'ChanServ'):
            user_box = UserBox(size_hint_y=None, height=40)
            user_box.lbl.bind(on_touch_down=user_box.on_label_touch_down)
            user_box.lbl.text = "{}: {}".format(user.username, char)
            user_box.pm.id = user.username
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
        user_box.set_sub_label("")

    def update_subloc(self, username, subloc):
        user_box = self.online_users.get(username, None)
        if user_box is None:
            return
        user_box.set_sub_label(subloc)

    def open_private_msg_screen(self, username, pm):  # Opens the PM window
        self.chat.pm_window_open_flag = True
        self.restore_pm_button_to_normal(pm)
        self.chat.build_conversation(username)
        self.chat.set_current_conversation_user(username)
        self.chat.open()
        pm_open_sound = SoundLoader.load('sounds/general/codecopen.mp3')
        App.get_running_app().play_sound(pm_open_sound, volume=self.pm_open_sound_volume)

    def restore_pm_button_to_normal(self, pm):
        pm.background_normal = 'atlas://data/images/defaulttheme/button'

    def muted_sender(self, pm, muted_users):  # Checks whether the sender of a pm is muted
        for x in range(len(muted_users)):
            if pm.sender == muted_users[x].username:
                return True
        return False

    def update_private_messages(self, *args):  # Acts on arrival of PMs
        main_scr = App.get_running_app().get_main_screen()
        irc = main_scr.manager.irc_connection
        pm = irc.get_pm()
        if pm is not None:
            if pm.sender != self.chat.username:
                if not self.muted_sender(pm, self.muted_users):
                    if not self.chat.pm_window_open_flag:
                        for btn in self.pm_buttons:
                            if pm.sender == btn.id:
                                btn.background_normal = 'atlas://data/images/defaulttheme/button_pressed'
                                break
                        if not self.chat.pm_flag and not self.chat.pm_window_open_flag:
                            pm_notif = SoundLoader.load('sounds/general/codeccall.mp3')
                            App.get_running_app().play_sound(pm_notif, volume=self.pm_notif_volume)
                            App.get_running_app().flash_window()
                            if not Window.focus:
                                App.get_running_app().notification("Mystery Online",
                                                                   "You've got a PM from {0}".format(pm.sender))
                    self.chat.pm_flag = True
                    self.chat.build_conversation(pm.sender)
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
            # TODO don't delete if it has a PM widnow that wasn't seen
        except KeyError:
            return
        self.user_list.remove_widget(label)
        del self.online_users[username]

    def on_ooc_checked(self, *args):
        self.ooc_chat_header.background_normal = 'atlas://data/images/defaulttheme/button'
        self.ooc_chat_header.background_color = [1, 1, 1, 1]

    def update_ooc(self, msg, sender, local=False):
        ref = msg
        if sender == 'default':
            sender = App.get_running_app().get_user().username
        if 'www.' in msg or 'http://' in msg or 'https://' in msg:
            msg = "[u]{}[/u]".format(msg)
        if self.counter == 100:
            self.counter = 0
            self.ooc_chat = OOCLogLabel()
            self.chat_grid.add_widget(self.ooc_chat)
            main_scr = App.get_running_app().get_main_screen()
            self.ooc_chat.bind(on_ref_press=main_scr.log_window.copy_text)
        if not local:
            self.ooc_chat.text += "{0}: [ref={2}]{1}[/ref]\n".format(sender, msg, escape_markup(ref))
        else:
            self.ooc_chat.text += "[color=adffff]{0}: [ref={2}]{1}[/ref][/color]\n".format(sender, msg,
                                                                                           escape_markup(ref))
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
                App.get_running_app().play_sound(self.ooc_notif, volume=self.ooc_notif.volume)
                config = App.get_running_app().config
                delay = config.getdefaultint('other', 'ooc_notif_delay', 60)
                Clock.schedule_once(self.ooc_time_callback, delay)
                self.ooc_play = False

    def ooc_time_callback(self, *args):
        self.ooc_play = True

    def send_ooc(self):
        if len(self.ooc_input.text) > 400:
            popup = MOPopup("Warning", "Message too long", "OK")
            popup.open()
            return
        if self.ooc_input.text != "":
            Clock.schedule_once(self.refocus_text)
            msg = self.ooc_input.text
            user_handler: CurrentUserHandler = App.get_running_app().get_user_handler()
            connection_manager = user_handler.get_connection_manager()
            message_factory = App.get_running_app().get_message_factory()
            if self.ooc_input.text[0] == ";":
                message = message_factory.build_looc_message(user_handler.current_loc.name, msg[1:])
            else:
                message = message_factory.build_ooc_message(msg)
            try:
                connection_manager.send_msg(message)
                connection_manager.send_local(message)
            except Exception as e:
                popup = MOPopup("Warning", "Something went wrong. " + str(e), "OK")
                popup.open()
            self.ooc_input.text = ""

    def refocus_text(self, *args):
        self.ooc_input.focus = True
