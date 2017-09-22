import random
import re

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.textinput import TextInput
from kivy.utils import escape_markup

from character_select import CharacterSelect
from irc_mo import PrivateConversation
from location import locations


class LeftTab(TabbedPanel):
    sprite_preview = ObjectProperty(None)
    sprite_settings = ObjectProperty(None)
    trans_slider = ObjectProperty(None)
    speed_slider = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LeftTab, self).__init__(**kwargs)

    def ready(self, main_scr):
        main_scr.sprite_preview = self.sprite_preview
        main_scr.sprite_settings = self.sprite_settings
        config = App.get_running_app().config
        self.trans_slider.value = config.getdefaultint('other', 'textbox_transparency', 60)
        self.speed_slider.value = config.getdefaultint('other', 'textbox_speed', 60)

    def on_trans_slider_value(self, *args):
        config = App.get_running_app().config
        value = int(self.trans_slider.value)
        config.set('other', 'textbox_transparency', value)

    def on_speed_slider_value(self, *args):
        config = App.get_running_app().config
        value = int(self.speed_slider.value)
        config.set('other', 'textbox_speed', value)


class Toolbar(BoxLayout):
    def __init__(self, **kwargs):
        super(Toolbar, self).__init__(**kwargs)
        self.main_btn = None
        self.main_loc_btn = None
        self.subloc_drop = DropDown(size_hint=(None, None), size=(200, 30))
        self.pos_drop = DropDown(size_hint=(None, None), size=(100, 30))
        for pos in ('center', 'right', 'left'):
            btn = Button(text=pos, size_hint=(None, None), size=(100, 30))
            btn.bind(on_release=lambda btn_: self.pos_drop.select(btn_.text))
            self.pos_drop.add_widget(btn)
        self.color_drop = DropDown(size_hint=(None, None), size=(200, 30))
        for col in ('red', 'blue', 'golden', 'green', 'FUCKING RAINBOW', 'normal'):
            btn = Button(text=col, size_hint=(None, None), size=(200, 30))
            btn.bind(on_release=lambda btn_: self.color_drop.select(btn_.text))
            self.color_drop.add_widget(btn)
        self.text_col_btn = Button(text='color', size_hint=(None, None), size=(200, 30))
        self.text_col_btn.bind(on_release=self.color_drop.open)
        self.add_widget(self.text_col_btn)
        self.color_drop.bind(on_select=self.on_col_select)
        self.pos_btn = Button(size_hint=(None, None), size=(100, 30))
        self.pos_btn.text = 'center'
        self.pos_btn.bind(on_release=self.pos_drop.open)
        self.add_widget(self.pos_btn)
        self.pos_drop.bind(on_select=self.on_pos_select)
        self.loc_drop = DropDown(size_hint=(None, None), size=(200, 30))

    def update_sub(self, loc):
        if self.main_btn is not None:
            self.subloc_drop.clear_widgets()
        for sub in loc.list_sub():
            btn = Button(text=sub, size_hint=(None, None), size=(200, 30))
            btn.bind(on_release=lambda btn_: self.subloc_drop.select(btn_.text))
            self.subloc_drop.add_widget(btn)
        if self.main_btn is None:
            self.main_btn = Button(size_hint=(None, None), size=(200, 30))
            self.main_btn.bind(on_release=self.subloc_drop.open)
            self.add_widget(self.main_btn)
            self.subloc_drop.bind(on_select=self.on_subloc_select)
        self.main_btn.text = loc.get_first_sub()

    def update_loc(self):
        for l in locations:
            btn = Button(text=l, size_hint=(None, None), size=(200, 30))
            btn.bind(on_release=lambda btn_: self.loc_drop.select(btn_.text))
            self.loc_drop.add_widget(btn)
        self.main_loc_btn = Button(size_hint=(None, None), size=(200, 30))
        user_handler = App.get_running_app().get_user_handler()
        current_loc = user_handler.get_current_loc()
        self.main_loc_btn.text = current_loc.name
        self.main_loc_btn.bind(on_release=self.loc_drop.open)
        self.add_widget(self.main_loc_btn)
        self.loc_drop.bind(on_select=self.on_loc_select)

    def on_loc_select(self, inst, loc_name):
        self.main_loc_btn.text = loc_name
        main_scr = self.parent.parent  # fug u
        user_handler = App.get_running_app().get_user_handler()
        loc = locations[loc_name]
        user_handler.set_current_loc(loc)
        self.update_sub(loc)
        main_scr.sprite_preview.set_subloc(user_handler.get_current_subloc())

    def on_subloc_select(self, inst, subloc_name):
        self.main_btn.text = subloc_name
        main_scr = App.get_running_app().get_main_screen()
        user_handler = App.get_running_app().get_user_handler()
        user_handler.set_current_subloc_name(subloc_name)
        sub = user_handler.get_current_subloc()
        main_scr.sprite_preview.set_subloc(sub)
        main_scr.refocus_text()

    def on_pos_select(self, inst, pos):
        self.pos_btn.text = pos
        main_scr = self.parent.parent  # I will never forgive Kivy
        user_handler = App.get_running_app().get_user_handler()
        user_handler.set_current_pos_name(pos)
        main_scr.refocus_text()

    def on_col_select(self, inst, col, user=None):
        self.text_col_btn.text = col
        main_scr = self.parent.parent  # I will never forgive Kivy either
        if user is None:
            user = self.parent.parent.user
        user.set_color(col)
        if user.color != 'ffffff':
            user.colored = True
        else:
            user.colored = False
        main_scr.refocus_text()


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


class PrivateMessageScreen(ModalView):
    pm_body = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PrivateMessageScreen, self).__init__(**kwargs)
        self.conversations = []
        self.irc = None
        self.username = ''
        self.current_conversation = None
        self.conversation_list = getattr(self.ids, 'prv_users_list')
        self.text_box = getattr(self.ids, 'pm_input')
        self.pm_close_sound = SoundLoader.load('sounds/general/codecover.wav')

    def ready(self):
        main_scr = App.get_running_app().get_main_screen()
        self.pm_body.bind(on_ref_press=main_scr.log_window.copy_text)

    def set_current_conversation(self, conversation):
        self.current_conversation = conversation

    def open_conversation(self, conversation):
        self.set_current_conversation(conversation)
        self.update_pms()

    def get_conversation_for_user(self, username):
        if len(self.conversations) is 0:
            self.build_conversation(username)
            return self.get_conversation_for_user(username)
        else:
            for c in self.conversations:
                if c.username == username:
                    return c

    def set_current_conversation_user(self, username):
        conversation = self.get_conversation_for_user(username)
        self.current_conversation = conversation

    def prv_chat_close_btn(self):
        vol = App.get_running_app().config.getdefaultint('sound', 'effect_volume', 100)
        self.pm_close_sound.volume = vol / 100
        self.pm_close_sound.play()
        self.dismiss()

    def build_conversation(self, username):
        is_init = False
        if username is not self.username:
            for c in self.conversations:
                if username == c.username:
                    is_init = True
            if not is_init:
                self.add_conversation(username)

    def add_conversation(self, username):
        conversation = PrivateConversation()
        conversation.username = username
        self.conversations.append(conversation)
        btn = Button(text=username, size_hint_y=None, height=50, width=self.conversation_list.width)
        btn.bind(on_press=lambda x: self.open_conversation(conversation))
        self.conversation_list.add_widget(btn)
        self.current_conversation = conversation

    def update_conversation(self, sender, msg):
        if 'www.' in msg or 'http://' in msg or 'https://' in msg:
            msg = "[u]{}[/u]".format(msg)
        self.current_conversation.msgs += "{0}: [ref={2}]{1}[/ref]\n".format(sender, msg, escape_markup(msg))
        self.update_pms()

    def update_pms(self):
        self.pm_body.text = self.current_conversation.msgs
        self.pm_body.parent.scroll_y = 0

    def refocus_text(self, *args):
        self.text_box.focus = True

    def send_pm(self):
        sender = self.username
        if self.current_conversation is not None:
            receiver = self.current_conversation.username
            self.irc.send_private_msg(receiver, sender, self.text_box.text)
            msg = self.text_box.text
            if 'www.' in msg or 'http://' in msg or 'https://' in msg:
                msg = "[u]{}[/u]".format(msg)
            self.current_conversation.msgs += "{0}: [ref={2}]{1}[/ref]\n".format(sender, msg, escape_markup(msg))
            self.pm_body.text = self.current_conversation.msgs
            self.text_box.text = ''
            self.pm_body.parent.scroll_y = 0
            Clock.schedule_once(self.refocus_text, 0.1)


class RightClickMenu(ModalView):
    char_select = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(RightClickMenu, self).__init__(**kwargs)

    def on_char_select_clicked(self, *args):
        cs = CharacterSelect()
        self.dismiss()
        cs.bind(on_dismiss=self.on_picked)
        cs.open()

    def on_settings_clicked(self, *args):
        App.get_running_app().open_settings()
        self.dismiss()

    def on_picked(self, inst):
        user = App.get_running_app().get_user()
        if inst.picked_char is not None:
            user.set_char(inst.picked_char)
            user.get_char().load()
            main_scr = App.get_running_app().get_main_screen()
            main_scr.on_new_char(user.get_char())


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


class MainScreen(Screen):
    icons_layout = ObjectProperty(None)
    sprite_preview = ObjectProperty(None)
    sprite_window = ObjectProperty(None)
    msg_input = ObjectProperty(None)
    toolbar = ObjectProperty(None)
    text_box = ObjectProperty(None)
    log_window = ObjectProperty(None)
    ooc_window = ObjectProperty(None)
    left_tab = ObjectProperty(None)
    sprite_settings = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.user = None
        self.users = {}
        App.get_running_app().set_main_screen(self)
        self.config = App.get_running_app().config

    def on_stop(self):
        pass

    def on_touch_down(self, touch):
        if touch.button == 'right':
            self.on_right_click(touch)
            return True
        super(MainScreen, self).on_touch_down(touch)

    def on_right_click(self, touch):
        menu = RightClickMenu()
        # Can't use absolute position so it uses a workaround
        menu_x = touch.pos[0] / Window.width
        menu_y = touch.pos[1] / Window.height
        if touch.pos[1] >= menu.height:
            loc_y = 'top'
        else:
            loc_y = 'y'
        menu.pos_hint = {'x': menu_x, loc_y: menu_y}
        menu.open()

    def on_ready(self, *args):
        """Called when mainscreen becomes active"""

        self.msg_input.ready(self)
        self.left_tab.ready(self)
        self.ooc_window.ready(self)
        self.log_window.ready()
        user_handler = App.get_running_app().get_user_handler()
        user_handler.set_current_loc(locations['Hakuryou'])
        self.toolbar.update_loc()
        self.toolbar.update_sub(locations['Hakuryou'])
        self.sprite_preview.set_subloc(user_handler.get_current_subloc())
        char = self.user.get_char()
        if char is not None:
            self.on_new_char(char)

    def on_new_char(self, char):
        self.msg_input.readonly = False
        self.icons_layout.load_icons(char.get_icons())
        self.set_first_sprite(char)
        user_handler = App.get_running_app().get_user_handler()
        connection_manager = user_handler.get_connection_manager()
        connection_manager.send_char_to_all(char.name)
        connection_manager.update_char(self, char.name, self.user.username)

    def set_first_sprite(self, char):
        first_icon = sorted(char.get_icons().textures.keys())[0]
        first_sprite = char.get_sprite(first_icon)
        self.sprite_preview.set_sprite(first_sprite)

    def refocus_text(self, *args):
        # Refocusing the text input has to be done this way cause Kivy
        self.msg_input.focus = True
