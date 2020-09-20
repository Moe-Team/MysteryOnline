import traceback

from kivy import Logger
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import escape_markup, platform
from kivy.resources import resource_find
import re
from MysteryOnline.commands import command_processor, CommandInvalidArgumentsError, CommandNoArgumentsError
from MysteryOnline.mopopup import MOPopup


class TextBox(Label):
    char_name = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(TextBox, self).__init__(**kwargs)
        self.msg = ""
        self.prev_user = None
        self.is_displaying_msg = False
        self.markup = True
        self.gen = None
        self.sfx = {}
        self.volume = 1.0
        self.sfx_volume = 1.0
        self.char_name_color = None
        self.char_name_rect = None
        self.textbox_color = None
        self.textbox_rect = None
        self.load_sounds()
        self.setup_volume()
        self.setup_textbox()

    def setup_textbox(self):
        with self.canvas.before:
            self.textbox_color = Color(rgba=[1, 1, 1, 0.6])
            self.textbox_rect = Rectangle(size=self.size, pos=self.pos, source="misc_img/TextBox.png")
        Clock.schedule_once(self.update_ui, 0)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def setup_volume(self):
        config = App.get_running_app().config  # The main config
        config.add_callback(self.on_volume_change, 'sound', 'blip_volume')
        config.add_callback(self.on_sfx_volume_change, 'sound', 'effect_volume')
        config.add_callback(self.on_trans_change, 'other', 'textbox_transparency')
        self.volume = App.get_running_app().exponential_volume(config.getdefaultint('sound', 'blip_volume', 100))
        self.sfx_volume = App.get_running_app().exponential_volume(config.getdefaultint('sound', 'effect_volume', 100))
        for sfx in self.sfx.values():
            sfx.volume = self.sfx_volume
        self.sfx["ffffff"].volume = self.volume

    def load_sounds(self):
        # TODO: Make this less hardcoded.
        self.sfx["ff3333"] = self.load_wav('sounds/general/red.mp3')
        self.sfx["00adfc"] = self.load_wav('sounds/general/blue.mp3')
        self.sfx["ffd700"] = self.load_wav('sounds/general/gold.mp3')
        self.sfx["00cd00"] = self.load_wav('sounds/general/green.mp3')
        self.sfx["8b6fba"] = self.load_wav('sounds/general/purple.mp3')
        self.sfx["rainbow"] = self.load_wav('sounds/general/rainbow.mp3')
        self.sfx["ffffff"] = self.load_wav('sounds/general/blip.wav')
        if platform != "win":
            self.sfx["ffffff"].load()

    def load_wav(self, filename):
        """Use SDL2 to load wav files cuz it's better, but only on windows"""
        rfn = resource_find(filename)
        sound = None
        if rfn is not None:
            filename = rfn
        if platform == 'win':
            sound = SoundLoader.load(filename)
        else:
            sound = SoundLoader.load(filename)
            sound.unload()  # We don't need to keep these loaded all the time... On linux.
        return sound

    def update_ui(self, dt):
        with self.char_name.canvas.before:
            self.char_name_color = Color(rgba=[1, 1, 1, 0.6])
            self.char_name_rect = Rectangle(size=self.size, pos=self.pos, source="misc_img/BoxChar.png")

    def update_rect(self, *args):
        self.textbox_rect.pos = self.pos
        if self.char_name_rect is not None:
            self.char_name_rect.pos = self.char_name.pos
            self.char_name_rect.size = self.char_name.size
        self.textbox_rect.size = self.size

    def on_trans_change(self, s, k, v):
        self.textbox_color.rgba = [1, 1, 1, v / 100]
        self.char_name_color.rgba = [1, 1, 1, v / 100]

    def play_sfx(self, sfx_name):
        sfx = self.load_wav('sounds/sfx/{0}'.format(sfx_name))
        config = App.get_running_app().config
        if sfx_name != "blip":
            v = App.get_running_app().exponential_volume(config.getdefaultint('sound', 'effect_volume', 100))
        else:
            v = App.get_running_app().exponential_volume(config.getdefaultint('sound', 'blip_volume', 100))
        App.get_running_app().play_sound(sfx, volume=v)

    def display_text(self, msg, user, color, sender):
        self.is_displaying_msg = True
        if self.prev_user is not user or (len(self.text) + len(msg) > 240):
            self.clear_textbox()
        self.prev_user = user
        config = App.get_running_app().config
        if config.getint('display', 'rpg_mode') == 1:
            char_name = user.get_char().get_display_name()
            self.char_name.text = char_name
        else:
            self.char_name.text = user.username
        self.msg = msg
        user.color = color

        def text_gen(text):
            for c in text:
                yield c

        config = App.get_running_app().config
        if user.color == 'ffffff' and config.getint('other', 'instant_text') == 0:
            self.gen = text_gen(self.msg)
            config = App.get_running_app().config
            speed = config.getdefaultint('other', 'textbox_speed', 60)
            self.sfx["ffffff"].volume = self.volume
            Clock.schedule_interval(self._animate, 1.0 / speed)
        else:
            if user.color in self.sfx:
                App.get_running_app().play_sound(self.sfx[user.color], volume=self.sfx_volume)

            if user.color != 'rainbow':
                self.msg = "[color={}]{}[/color]".format(user.color, self.msg)
            else:
                self.msg = self.msg.replace("&bl;", "[")
                self.msg = self.msg.replace("&br;", "]")
                self.msg = self.msg.replace("&amp;", "&")
                msg_array = list(self.msg)
                self.msg = ''
                # ff5aac
                if config.getint("other", "suppress_rainbow") == 0:
                    color_spectrum = ['ff3333', 'ffa500', 'ffff00', '33cc33', '00adfc', '8b6fba', 'ee82ee']
                else:
                    color_spectrum = ['ff8181', 'ffd689', 'ffff89', 'a1e7a1', '86d9ff', 'b6a4d3', 'f093f0']
                y = 0

                for x in range(len(msg_array)):
                    if y == 7:
                        y = 0
                    col = color_spectrum[y]
                    self.msg += "[color={}]{}[/color]".format(col, escape_markup(msg_array[x]))
                    if msg_array[x] != ' ':
                        y = y + 1
            self.text = self.msg
            self.text += " "
            self.is_displaying_msg = False
        main_scr = App.get_running_app().get_main_screen()  # BLAAAME KIVYYYY
        main_scr.log_window.add_chat_entry(self.msg, user.username)
        if sender == "default":
            main_scr.toolbar.text_col_btn.text = 'color'
        user.color = 'ffffff'
        user.colored = False

    def _animate(self, dt):
        try:
            self.sfx["ffffff"].play()
            self.sfx["ffffff"].seek(0)
            self.text += next(self.gen)
        except StopIteration:
            self.text += " "
            self.is_displaying_msg = False
            return False

    def unload_blip(self, delta):
        if platform != "win":
            self.sfx["ffffff"].unload()

    def clear_textbox(self):
        self.text = ""

    def on_volume_change(self, s, k, v):
        self.volume = App.get_running_app().exponential_volume(v)
        try:
            self.sfx["ffffff"].volume = self.volume
        except AttributeError:
            pass

    def on_sfx_volume_change(self, s, k, v):
        self.sfx_volume = App.get_running_app().exponential_volume(v)
        try:
            for sfx_name in self.sfx:
                if sfx_name == "ffffff":
                    continue
                sfx = self.sfx[sfx_name]
                sfx.volume = self.sfx_volume * 0.5
        except AttributeError:
            pass


class MainTextInput(TextInput):
    def __init__(self, **kwargs):
        super(MainTextInput, self).__init__(**kwargs)
        self.icon_change_spam = False

    def ready(self, main_screen):
        Clock.schedule_once(main_screen.refocus_text)

    def enable_icon_change(self, dt=None):
        self.icon_change_spam = False

    def send_message(self, *args):
        if len(self.text) > 250:
            popup = MOPopup("Warning", "Message too long", "OK")
            popup.open()
            return
        elif len(self.text) == 0 and not self.icon_change_spam:
            self.icon_change_spam = True
            Clock.schedule_once(self.enable_icon_change, 0.25)
            App.get_running_app().get_user_handler().send_icon()
            return
        main_scr = App.get_running_app().get_main_screen()
        Clock.schedule_once(main_scr.refocus_text)
        msg = escape_markup(self.text)
        if not self.message_is_valid(msg):
            return
        self.text = ""
        msg = self.extend_message(msg)
        if self.message_is_command(msg):
            try:
                self.handle_command(msg)
            except (AttributeError, IndexError) as e:
                Logger.warning(traceback.format_exc())
                return
        else:
            user_handler = App.get_running_app().get_user_handler()
            try:
                user_handler.send_message(msg)
            except Exception as e:
                popup = MOPopup("Warning", "Something went wrong. "+str(e), "OK")
                popup.open()

    def message_is_valid(self, msg):
        pattern = re.compile(r'\s+')
        match = re.fullmatch(pattern, msg)
        if msg == '' or match:
            return False
        return True

    def message_is_command(self, msg):
        if msg.startswith('/'):
            words = msg.split(' ')
            if words[0][1:] in command_processor.get_commands():
                return True
        return False

    def extend_message(self, msg):
        for shortcut in command_processor.shortcuts:
            if self.message_is_shortcut(msg, shortcut):
                msg = msg.replace(shortcut, command_processor.shortcuts[shortcut], 1) + "'"
                return msg
        return msg

    def message_is_shortcut(self, msg, shortcut):
        return msg.startswith(shortcut) and\
               not any(msg.startswith('/'+command) for command in command_processor.get_commands())

    def handle_command(self, msg):
        try:
            cmd_name, cmd = msg.split(' ', 1)
        except ValueError:
            cmd_name = msg
            cmd = None
        cmd_name = cmd_name[1:]
        try:
            command_processor.process_command(cmd_name, cmd)
        except CommandInvalidArgumentsError:
            Logger.warning("Invalid arguments")
            pass
        except CommandNoArgumentsError:
            Logger.warning("No arguments given")
            pass

    def cursor_offset(self):
        """Fix weird kivy bug when col sometimes isn't an int"""
        offset = 0
        row = self.cursor_row
        col = self.cursor_col
        col = int(col)
        _lines = self._lines
        if col and row < len(_lines):
            offset = self._get_text_width(
                _lines[row][:col], self.tab_width,
                self._label_cached)
        return offset
