import random
import re

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import escape_markup


class TextBox(Label):
    char_name = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(TextBox, self).__init__(**kwargs)
        self.msg = ""
        self.prev_user = None
        self.is_displaying_msg = False
        self.markup = True
        self.gen = None
        self.blip = SoundLoader.load('sounds/general/blip.wav')
        self.red_sfx = SoundLoader.load('sounds/general/red.wav')
        self.blue_sfx = SoundLoader.load('sounds/general/blue.wav')
        self.gold_sfx = SoundLoader.load('sounds/general/gold.wav')
        config = App.get_running_app().config  # The main config
        config.add_callback(self.on_volume_change, 'sound', 'blip_volume')
        config.add_callback(self.on_trans_change, 'other', 'textbox_transparency')
        vol = config.getdefaultint('sound', 'blip_volume', 100) / 100
        self.blip.volume = vol
        self.red_sfx.volume = vol * 0.5
        self.blue_sfx.volume = vol * 0.5
        self.gold_sfx.volume = vol * 0.5
        self.char_name_color = None
        self.char_name_rect = None
        with self.canvas.before:
            self.textbox_color = Color(rgba=[1, 1, 1, 0.6])
            self.textbox_rect = Rectangle(size=self.size, pos=self.pos, source="misc_img\\TextBox.png")
        Clock.schedule_once(self.update_ui, 0)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_ui(self, dt):
        with self.char_name.canvas.before:
            self.char_name_color = Color(rgba=[1, 1, 1, 0.6])
            self.char_name_rect = Rectangle(size=self.size, pos=self.pos, source="misc_img\\BoxChar.png")

    def update_rect(self, *args):
        self.textbox_rect.pos = self.pos
        if self.char_name_rect is not None:
            self.char_name_rect.pos = self.char_name.pos
            self.char_name_rect.size = self.char_name.size
        self.textbox_rect.size = self.size

    def on_trans_change(self, s, k, v):
        self.textbox_color.rgba = [1, 1, 1, v / 100]
        self.char_name_color.rgba = [1, 1, 1, v / 100]

    def command_identifier(self, msg):
        msg = msg[1:]
        command = msg.split(' ')[0]
        if command != ' ':
            return command

    def int_to_str_in_box(self, num):
        boxed = '(' + str(num) + ') '
        return boxed

    def fate_calculator(self, fate):
        result = 0
        for x in range(len(fate)):
            if fate[x] == '(+)':
                result = result + 1
            if fate[x] == '(-)':
                result = result - 1
        return result

    def command_handler(self, msg, command):
        main_scr = self.parent.parent
        user = main_scr.user
        if command == 'roll':
            modifier_flag = False
            roll_regex = re.compile(r'(\d)d(\d*)\+*(\d+)')
            fate_regex = re.compile(r'(\d)df')
            roll_search = roll_regex.search(msg)
            fate_search = fate_regex.search(msg)
            if roll_search is None:
                if fate_search is None:
                    return
                else:
                    fate_values = fate_search.group(0).split('d', 1)
                    fate_number = fate_values[0]
                    fates = '(0)', '(+)', '(-)'
                    fate_results = []
                    for unused in range(int(fate_number)):
                        fate_results.append(random.choice(fates))
                    fate_results_str = ''.join(str(e) for e in fate_results)
                    main_scr.log_window.add_entry('Rolled ' + fate_number + 'df ' 'and got: ' +
                                                  fate_results_str + '= ' + str(self.fate_calculator(fate_results)),
                                                  '[' + user.username + ']')
            else:
                dice_values = roll_search.group(0).split('d', 1)
                dice_number = dice_values[0]
                if '+' in dice_values[1]:
                    dice_values = dice_values[1].split('+', 1)
                    dice_sides = dice_values[0]
                    dice_modifier = dice_values[1]
                    modifier_flag = True
                else:
                    dice_sides = dice_values[1]
                dice_results = []
                for unused in range(0, int(dice_number)):
                    dice_results.append(random.randint(1, int(dice_sides)))
                dice_results_on_str = ''.join(self.int_to_str_in_box(e) for e in dice_results)
                if modifier_flag:
                    main_scr.log_window.add_entry('Rolled ' + dice_number + 'd' + dice_sides + ' and got: '
                                                  + dice_results_on_str + '+' + dice_modifier + '= ' +
                                                  str(sum(dice_results)+int(dice_modifier)), '[' + user.username + ']')
                else:
                    main_scr.log_window.add_entry('Rolled ' + dice_number+'d' + dice_sides + ' and got: '
                                                  + dice_results_on_str + '= ' + str(sum(dice_results)), '[' + user.username + ']')

    def display_text(self, msg, user, color, sender):
        self.is_displaying_msg = True
        if self.prev_user is not user:
            self.text = ""
        self.prev_user = user
        char_name = user.get_char().name
        self.char_name.text = char_name
        self.msg = msg
        user.color = color

        def text_gen(text):
            for c in text:
                yield c

        if user.color == 'ffffff':
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
            else:
                msg_array = list(self.msg)
                self.msg = ''
                why_wont_you_let_me_do_this_in_a_single_function_python_pls = len(msg_array)
                color_spectrum = ['ff3333', 'ffa500', 'ffff00', '33cc33', '00adfc', '8b6fba', 'ee82ee']
                y = 0
                for x in range(why_wont_you_let_me_do_this_in_a_single_function_python_pls):
                    if y == 7:
                        y = 0
                    col = color_spectrum[y]
                    self.msg += "[color={}]{}[/color]".format(col, msg_array[x])
                    if msg_array[x] != ' ':
                        y = y + 1
            self.text = self.msg
            self.text += " "
            self.is_displaying_msg = False
        main_scr = self.parent.parent  # BLAAAME KIVYYYY
        main_scr.log_window.add_entry(self.msg, user.username)
        if user.username == sender:
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

    def on_volume_change(self, s, k, v):
        vol = int(v) / 100
        self.blip.volume = vol
        self.red_sfx.volume = vol * 0.5
        self.blue_sfx.volume = vol * 0.5
        self.gold_sfx.volume = vol * 0.5


class MainTextInput(TextInput):

    def __init__(self, **kwargs):
        super(MainTextInput, self).__init__(**kwargs)

    def ready(self, main_screen):
        Clock.schedule_once(main_screen.refocus_text)

    def send_message(self, *args):
        main_scr = App.get_running_app().get_main_screen()
        Clock.schedule_once(main_scr.refocus_text, 0.2)
        msg = escape_markup(self.text)
        if not self.is_message_valid(msg):
            return
        self.text = ""
        user_handler = App.get_running_app().get_user_handler()
        user_handler.send_message(msg)

    def is_message_valid(self, msg):
        pattern = re.compile(r'\s+')
        match = re.fullmatch(pattern, msg)
        if msg == '' or match:
            return False
        return True