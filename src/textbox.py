from kivy.app import App
from kivy.clock import Clock
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import escape_markup
from kivy.resources import resource_find
from kivy.core.audio.audio_sdl2 import SoundSDL2

import re
from commands import command_processor, CommandInvalidArgumentsError, CommandNoArgumentsError
from mopopup import MOPopup


class TextBox(Label):
    char_name = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(TextBox, self).__init__(**kwargs)
        self.msg = ""
        self.prev_user = None
        self.is_displaying_msg = False
        self.markup = True
        self.gen = None
        self.blip = None
        self.red_sfx = None
        self.blue_sfx = None
        self.gold_sfx = None
        self.green_sfx = None
        self.purple_sfx = None
        self.rainbow_sfx = None
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
        config.add_callback(self.on_trans_change, 'other', 'textbox_transparency')
        vol = config.getdefaultint('sound', 'blip_volume', 100) / 100
        self.blip.volume = vol
        self.red_sfx.volume = vol * 0.5
        self.blue_sfx.volume = vol * 0.5
        self.gold_sfx.volume = vol * 0.5
        self.green_sfx.volume = vol * 0.5
        self.purple_sfx.volume = vol * 0.5
        self.rainbow_sfx.volume = vol * 0.5

    def load_sounds(self):
        self.blip = self.load_wav('sounds/general/blip.mp3')
        self.red_sfx = self.load_wav('sounds/general/red.mp3')
        self.blue_sfx = self.load_wav('sounds/general/blue.mp3')
        self.gold_sfx = self.load_wav('sounds/general/gold.mp3')
        self.green_sfx = self.load_wav('sounds/general/green.mp3')
        self.purple_sfx = self.load_wav('sounds/general/purple.mp3')
        self.rainbow_sfx = self.load_wav('sounds/general/rainbow.mp3')

    def load_wav(self, filename):
        """Use SDL2 to load wav files cuz it's better"""
        rfn = resource_find(filename)
        if rfn is not None:
            filename = rfn
        return SoundSDL2(source=filename)

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
        vol = config.getdefaultint('sound', 'effect_volume', 100) / 100
        sfx.volume = vol
        sfx.play()

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
            Clock.schedule_interval(self._animate, 1.0 / speed)
        else:
            if user.color != 'rainbow':
                self.msg = "[color={}]{}[/color]".format(user.color, self.msg)
                if user.color == 'ff3333':
                    self.red_sfx.play()
                elif user.color == '00adfc':
                    self.blue_sfx.play()
                elif user.color == 'ffd700':
                    self.gold_sfx.play()
                elif user.color == '8b6fba':
                    self.purple_sfx.play()
                elif user.color == '00cd00':
                    self.green_sfx.play()
                elif user.color == 'ffffff':
                    self.blip.play()
            else:
                self.rainbow_sfx.play()
                msg_array = list(self.msg)
                self.msg = ''
                color_spectrum = ['ff3333', 'ffa500', 'ffff00', '33cc33', '00adfc', '8b6fba', 'ee82ee']
                y = 0
                for x in range(len(msg_array)):
                    if y == 7:
                        y = 0
                    col = color_spectrum[y]
                    self.msg += "[color={}]{}[/color]".format(col, msg_array[x])
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
            self.blip.play()
            self.text += next(self.gen)
        except StopIteration:
            self.text += " "
            self.is_displaying_msg = False
            return False

    def clear_textbox(self):
        self.text = ""

    def on_volume_change(self, s, k, v):
        vol = int(v) / 100
        self.blip.volume = vol
        self.red_sfx.volume = vol * 0.5
        self.blue_sfx.volume = vol * 0.5
        self.gold_sfx.volume = vol * 0.5
        self.green_sfx.volume = vol * 0.5
        self.purple_sfx.volume = vol * 0.5
        self.rainbow_sfx.volume = vol * 0.5


class MainTextInput(TextInput):
    def __init__(self, **kwargs):
        super(MainTextInput, self).__init__(**kwargs)

    def ready(self, main_screen):
        Clock.schedule_once(main_screen.refocus_text)

    def send_message(self, *args):
        if len(self.text) > 400:
            popup = MOPopup("Warning", "Message too long", "OK")
            popup.open()
            return
        main_scr = App.get_running_app().get_main_screen()
        Clock.schedule_once(main_scr.refocus_text)
        msg = escape_markup(self.text)
        if not self.message_is_valid(msg):
            return
        self.text = ""
        msg = self.extend_message(msg)
        if self.message_is_command(msg):
            self.handle_command(msg)
        else:
            user_handler = App.get_running_app().get_user_handler()
            user_handler.send_message(msg)

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
            print("Invalid arguments")
            pass
        except CommandNoArgumentsError:
            print("No arguments given")
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
