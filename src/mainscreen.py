from kivy.app import App
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.dropdown import DropDown
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.utils import escape_markup
from character import characters
from user import User
from location import locations
from character_select import CharacterSelect
from irc_mo import PrivateConversation
import re
import webbrowser
import threading
import requests
from datetime import datetime


class SpriteSettings(BoxLayout):
    check_flip_h = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SpriteSettings, self).__init__(**kwargs)
        self.functions = {"flip_h": self.flip_sprite}
        self.activated = []
        self.flipped = []

    def ready(self):
        self.check_flip_h.bind(active=self.on_check_flip_h)

    def apply_post_processing(self, sprite, setting):
        if setting == 0:
            if sprite not in self.flipped:
                self.flip_sprite(sprite)
                self.flipped.append(sprite)
        else:
            if sprite in self.flipped:
                self.flip_sprite(sprite)
                self.flipped.remove(sprite)
        return sprite

    def flip_sprite(self, sprite):
        sprite.flip_horizontal()

    def on_check_flip_h(self, c, value):
        main_scr = App.get_running_app().get_main_screen()
        if value == 1:
            main_scr.current_sprite_option = 0
        else:
            main_scr.current_sprite_option = -1


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
        self.main_loc_btn.text = self.parent.parent.current_loc.name
        self.main_loc_btn.bind(on_release=self.loc_drop.open)
        self.add_widget(self.main_loc_btn)
        self.loc_drop.bind(on_select=self.on_loc_select)

    def on_loc_select(self, inst, loc):
        self.main_loc_btn.text = loc
        main_scr = self.parent.parent  # fug u
        main_scr.current_loc = locations[loc]

    def on_subloc_select(self, inst, subloc):
        self.main_btn.text = subloc
        main_scr = self.parent.parent  # Always blame Kivy
        main_scr.current_subloc = subloc
        main_scr.refocus_text()

    def on_pos_select(self, inst, pos):
        self.pos_btn.text = pos
        main_scr = self.parent.parent  # I will never forgive Kivy
        main_scr.current_pos = pos
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


class Icon(Image):
    def __init__(self, name, ic, **kwargs):
        super(Icon, self).__init__(**kwargs)
        self.texture = ic
        self.name = name
        self.size_hint = (None, None)
        self.size = (40, 40)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.parent.sprite_picked(self, self.name)
            return True

    def on_mouse_pos(self, *args):
        if not self.parent or not self.parent.parent:
            return
        if not self.get_root_window():
            return
        pos = args[1]
        Clock.unschedule(self.display_tooltip)  # cancel scheduled event since I moved the cursor
        self.close_tooltip()  # close if it's opened
        if self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.display_tooltip, 1)
            self.parent.scheduled_icon = self

    def display_tooltip(self, *args):
        if not self.parent or not self.parent.parent:
            return
        if len(Window.children) > 1:
            return
        self.parent.parent.on_hover_in(self.name)

    def close_tooltip(self, *args):
        if not self.parent or not self.parent.parent:
            return
        self.parent.parent.on_hover_out()


# noinspection PyTypeChecker
class IconsLayout(BoxLayout):
    current_page = NumericProperty(1)

    def __init__(self, **kwargs):
        super(IconsLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.grids = []
        self.current_icon = None
        self.hover_popup = ModalView(size_hint=(None, None), background_color=[0, 0, 0, 0],
                                     background='misc_img/transparent.png')
        self.scheduled_icon = None
        self.max_pages = 0
        self.loading = False

    def prev_page(self, *args):
        if self.current_page > 1:
            self.current_page -= 1

    def next_page(self, *args):
        if self.current_page < self.max_pages:
            self.current_page += 1

    def on_current_page(self, *args):
        if not self.loading:
            self.remove_widget(self.children[1])
            grid_index = self.current_page - 1
            self.add_widget(self.grids[grid_index], index=1)

    def load_icons(self, icons):
        if len(self.children) > 1:
            self.remove_widget(self.children[1])
        for g in self.grids:
            g.clear_widgets()
        del self.grids[:]
        counter = 0
        g = None
        for i in sorted(icons.textures.keys()):
            if counter % 48 == 0:
                g = GridLayout(cols=6)
                self.grids.append(g)
            g.add_widget(Icon(i, icons[i]))
            counter += 1
        self.max_pages = len(self.grids)
        self.loading = True
        self.current_page = 1
        self.add_widget(self.grids[0], index=1)
        self.sprite_picked(self.grids[0].children[-1])
        self.loading = False

    def sprite_picked(self, icon, sprite_name=None):
        if sprite_name is None:
            sprite_name = icon.name
        main_scr = self.parent.parent  # blame kivy
        main_scr.current_sprite = sprite_name
        if self.current_icon is not None:
            self.current_icon.color = [1, 1, 1, 1]
        icon.color = [0.3, 0.3, 0.3, 1]
        self.current_icon = icon

    def on_hover_in(self, sprite_name):
        if self.hover_popup.get_parent_window():
            return
        main_scr = self.parent.parent
        char = main_scr.user.get_char()
        sprite = char.get_sprite(sprite_name, True)
        sprite_size = sprite.size
        # Can't use absolute position so it uses a workaround
        hover_x = self.right / Window.width
        hover_y = self.y / Window.height
        sprite_size = sprite_size[0] * 0.8, sprite_size[1] * 0.8
        im = Image()
        im.texture = sprite
        im.size = sprite.size
        self.hover_popup.add_widget(im)
        self.hover_popup.size = sprite_size
        self.hover_popup.pos_hint = {'x': hover_x, 'y': hover_y}
        self.hover_popup.open()

    def on_hover_out(self):
        if self.hover_popup.get_parent_window():
            self.hover_popup.clear_widgets()
            self.hover_popup.dismiss(animation=False)

    def on_scroll_start(self, *args):
        super(IconsLayout, self).on_scroll_start(*args)
        if self.scheduled_icon:
            Clock.unschedule(self.scheduled_icon.display_tooltip)


class SpritePreview(Image):
    center_sprite = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SpritePreview, self).__init__(**kwargs)

    def set_subloc(self, sub):
        self.texture = sub.get_img().texture

    def set_sprite(self, sprite):
        self.center_sprite.texture = None
        self.center_sprite.texture = sprite
        self.center_sprite.opacity = 1
        self.center_sprite.size = (self.center_sprite.texture.width / 3,
                                   self.center_sprite.texture.height / 3)


class SpriteWindow(Widget):
    background = ObjectProperty(None)
    center_sprite = ObjectProperty(None)
    left_sprite = ObjectProperty(None)
    right_sprite = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SpriteWindow, self).__init__(**kwargs)

    def set_sprite(self, user):
        subloc = user.get_subloc()
        pos = user.get_pos()
        if pos == 'right':
            subloc.add_r_user(user)
        elif pos == 'left':
            subloc.add_l_user(user)
        else:
            subloc.add_c_user(user)
        self.display_sub(subloc)

    def set_subloc(self, subloc):
        self.background.texture = subloc.get_img().texture

    def display_sub(self, subloc):
        if subloc.c_users:
            sprite = subloc.get_c_user().get_current_sprite()
            option = subloc.get_c_user().get_sprite_option()
            main_scr = self.parent.parent
            sprite = main_scr.sprite_settings.apply_post_processing(sprite, option)
            if sprite is not None:
                self.center_sprite.texture = None
                self.center_sprite.texture = sprite
                self.center_sprite.opacity = 1
                self.center_sprite.size = self.center_sprite.texture.size
        else:
            self.center_sprite.texture = None
            self.center_sprite.opacity = 0
        if subloc.l_users:
            sprite = subloc.get_l_user().get_current_sprite()
            option = subloc.get_l_user().get_sprite_option()
            main_scr = self.parent.parent
            sprite = main_scr.sprite_settings.apply_post_processing(sprite, option)
            if sprite is not None:
                self.left_sprite.texture = None
                self.left_sprite.texture = sprite
                self.left_sprite.opacity = 1
                self.left_sprite.size = self.left_sprite.texture.size
        else:
            self.left_sprite.texture = None
            self.left_sprite.opacity = 0
        if subloc.r_users:
            sprite = subloc.get_r_user().get_current_sprite()
            option = subloc.get_r_user().get_sprite_option()
            main_scr = self.parent.parent
            sprite = main_scr.sprite_settings.apply_post_processing(sprite, option)
            if sprite is not None:
                self.right_sprite.texture = None
                self.right_sprite.texture = sprite
                self.right_sprite.opacity = 1
                self.right_sprite.size = self.right_sprite.texture.size
        else:
            self.right_sprite.texture = None
            self.right_sprite.opacity = 0


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
        config = App.get_running_app().config  # The main config
        config.add_callback(self.on_volume_change, 'sound', 'blip_volume')
        config.add_callback(self.on_trans_change, 'other', 'textbox_transparency')
        self.blip.volume = config.getdefaultint('sound', 'blip_volume', 100) / 100
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
        self.textbox_color.rgba = [1, 1, 1, v/100]
        self.char_name_color.rgba = [1, 1, 1, v/100]

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
        self.blip.volume = int(v) / 100


class LogLabel(Label):
    def __init__(self, **kwargs):
        super(LogLabel, self).__init__(**kwargs)


class LogWindow(ScrollView):
    grid_l = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LogWindow, self).__init__(**kwargs)
        self.log = LogLabel()
        self.log.bind(on_ref_press=self.copy_text)
        self.counter = 0

    def ready(self):
        self.grid_l.bind(minimum_height=self.grid_l.setter('height'))
        self.grid_l.add_widget(self.log)

    def add_special_entry(self, msg):
        self.log.text += msg

    def add_entry(self, msg, username):
        if self.counter == 100:
            self.counter = 0
            self.log = LogLabel()
            self.grid_l.add_widget(self.log)
            self.log.bind(on_ref_press=self.copy_text)
        self.log.text += "{0}: [ref={2}]{1}[/ref]\n".format(username, msg, self.remove_markup(msg))
        self.counter += 1
        config = App.get_running_app().config
        if config.getdefaultint('other', 'log_scrolling', 1):
            self.scroll_y = 0
        now = datetime.now()
        cur_date = now.strftime("%d-%m-%Y")
        cur_time = now.strftime("%H:%M:%S")
        msg = self.remove_markup(msg)
        log_msg = "<{} {}> {}: {}\n".format(cur_time, cur_date, username, msg)
        with open('msg_log.txt', 'a', encoding='utf-8') as f:
            f.write(log_msg)

    def copy_text(self, inst, value):
        if 'www.' in value or 'http://' in value or 'https://' in value:
            pattern = re.compile(r'(https?://)?[-a-zA-Z0-9@:%._+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_+.~#?&/=]*)')
            url = re.search(pattern, value)
            if url:
                webbrowser.open(url.group(0))
            return
        value = value.replace('&bl;', '[').replace('&br;', ']').replace('&amp', '&')
        Clipboard.copy(value)

    def remove_markup(self, msg):
        pattern = re.compile(r'\[/?color.*?\]')
        msg = re.sub(pattern, '', msg)
        return msg


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


class OOCLogLabel(Label):
    def __init__(self, **kwargs):
        super(OOCLogLabel, self).__init__(**kwargs)


class OOCWindow(TabbedPanel):
    user_list = ObjectProperty(None)
    ooc_chat_header = ObjectProperty(None)
    ooc_input = ObjectProperty(None)
    blip_slider = ObjectProperty(None)
    music_slider = ObjectProperty(None)
    effect_slider = ObjectProperty(None)
    url_input = ObjectProperty(None)
    loop_checkbox = ObjectProperty(None)
    chat_grid = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(OOCWindow, self).__init__(**kwargs)
        self.online_users = {}
        self.track = None
        self.loop = True
        self.ooc_notif = SoundLoader.load('sounds/general/notification.mp3')
        self.ooc_play = True
        self.chat = PrivateMessageScreen()
        self.muted_users = []
        self.ooc_chat = OOCLogLabel()
        self.counter = 0

    def ready(self):
        main_scr = self.parent.parent
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
        self.loop_checkbox.bind(active=self.on_loop)
        self.ooc_chat_header.bind(on_press=self.on_ooc_checked)
        self.chat.ready()
        if self.chat.irc is None:
            self.chat.irc = self.parent.parent.manager.irc_connection
        self.chat.username = self.parent.parent.user.username
        Clock.schedule_interval(self.update_private_messages, 1.0 / 60.0)

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
        if self.track is not None:
            self.track.volume = value / 100
        config.set('sound', 'music_volume', value)

    def on_ooc_volume_change(self, s, k, v):
        self.effect_slider.value = v
        self.ooc_notif.volume = int(v) / 100

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
            user_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            lbl = Label(text="{}: {}\n".format(user.username, char), size_hint_y=None, size_hint_x=0.4, height=30)
            pm = Button(text="PM", size_hint_x=0.3, size_hint_y=None, height=30)
            mute = Button(text='Mute', size_hint_x=0.3, size_hint_y=None, height=30)
            pm.bind(on_press=lambda x: self.open_private_msg_screen(user.username, pm))
            mute.bind(on_press=lambda x: self.mute_user(user, mute))
            self.user_list.add_widget(user_box)
            user_box.add_widget(lbl)
            user_box.add_widget(pm)
            user_box.add_widget(mute)
            self.online_users[user.username] = user_box

    def open_private_msg_screen(self, username, pm):
        pm.background_color = (1, 1, 1, 1)
        self.chat.build_conversation(username)
        self.chat.set_current_conversation_user(username)
        self.chat.open()

    def update_private_messages(self, *args):
        main_scr = self.parent.parent
        irc = main_scr.manager.irc_connection
        pm = irc.get_pm()
        if pm is not None:
            if pm.sender != self.chat.username:
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

    def update_char(self, char, username):
        try:
            self.online_users[username].text = "{}: {}\n".format(username, char)
        except KeyError:
            pass

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

    def on_music_play(self, url=None):
        if url is None:
            url = self.url_input.text
            self.url_input.text = ""
            main_screen = self.parent.parent
            main_screen.update_music(url)
            main_screen.log_window.log.text += "You changed the music.\n"
            config = App.get_running_app().config
            if config.getdefaultint('other', 'log_scrolling', 1):
                main_screen.log_window.log.scroll_y = 0
        if not any(s in url.lower() for s in ('mp3', 'wav', 'ogg', 'flac')):
            print("Probably not music m8.")
            return

        def play_song(root):
            track = root.track
            if track is not None and track.state == 'play':
                track.stop()
            try:
                r = requests.get(url)
            except requests.exceptions.MissingSchema:
                print("Invalid url.")
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
    current_sprite = StringProperty("")
    current_loc = ObjectProperty(None)
    current_subloc = StringProperty("")
    current_pos = StringProperty("center")
    current_sprite_option = NumericProperty(-1)

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
        self.msg_input.readonly = True
        self.ooc_window.ooc_chat.bind(on_ref_press=self.log_window.copy_text)
        self.msg_input.bind(on_text_validate=self.send_message)
        Clock.schedule_once(self.refocus_text)
        self.ooc_window.add_user(self.user)
        self.left_tab.ready(self)
        self.ooc_window.ready()
        self.log_window.ready()
        self.sprite_settings.ready()
        self.current_loc = locations['Hakuryou']
        self.toolbar.update_loc()
        char = self.user.get_char()
        if char is not None:
            self.on_new_char(char)

    def on_new_char(self, char):
        self.msg_input.readonly = False
        self.icons_layout.load_icons(char.get_icons())
        first_icon = sorted(self.user.get_char().get_icons().textures.keys())[0]
        first_sprite = self.user.get_char().get_sprite(first_icon)
        self.sprite_preview.set_sprite(first_sprite)
        self.manager.irc_connection.send_special('char', char.name)
        self.update_char(char.name, self.user.username)

    def on_current_loc(self, *args):
        # Called when the current location changes
        self.user.set_loc(self.current_loc)
        subloc = self.current_loc.get_first_sub()
        self.current_subloc = subloc
        self.toolbar.update_sub(self.current_loc)

    def on_current_subloc(self, *args):
        # Called when the current sublocation changes
        subloc = self.current_loc.get_sub(self.current_subloc)
        self.user.set_subloc(subloc)
        self.sprite_preview.set_subloc(subloc)

    def on_current_pos(self, *args):
        pass

    def on_current_sprite(self, *args):
        # Called when user picks new sprite
        self.user.set_current_sprite(self.current_sprite)
        sprite = self.user.get_current_sprite()
        sprite = self.sprite_settings.apply_post_processing(sprite, self.current_sprite_option)
        self.sprite_preview.set_sprite(sprite)
        Clock.schedule_once(self.refocus_text, 0.2)

    def on_current_sprite_option(self, *args):
        self.user.set_sprite_option(self.current_sprite_option)
        sprite = self.user.get_current_sprite()
        sprite = self.sprite_settings.apply_post_processing(sprite, self.current_sprite_option)
        self.sprite_preview.set_sprite(sprite)
        Clock.schedule_once(self.refocus_text, 0.2)

    def send_message(self, *args):
        msg = escape_markup(self.msg_input.text)
        Clock.schedule_once(self.refocus_text)
        pattern = re.compile(r'\s+')
        match = re.fullmatch(pattern, msg)
        if msg == '' or match:
            return
        self.user.set_pos(self.current_pos)
        col_id = 0
        user = self.user
        if user.colored:
            col_id = self.user.color_ids.index(user.get_color())
        self.msg_input.text = ""
        loc = user.get_loc().name
        char = user.get_char().name
        sprite_option = user.get_sprite_option()
        self.manager.irc_connection.send_msg(msg, loc, self.current_subloc, char,
                                             self.current_sprite, self.current_pos, col_id, sprite_option)

    def refocus_text(self, *args):
        # Refocusing the text input has to be done this way cause Kivy
        self.msg_input.focus = True

    def update_chat(self, dt):
        if self.text_box.is_displaying_msg:
            return
        config = App.get_running_app().config
        msg = self.manager.irc_connection.get_msg()
        if msg is not None:
            if msg.identify() == 'chat':
                dcd = msg.decode()
                if dcd[0] == "default":
                    user = self.user
                else:
                    try:
                        user = self.users[dcd[0]]
                    except KeyError:
                        return
                    user.set_from_msg(*dcd)
                loc = dcd[1]
                if loc == self.current_loc.name and user not in self.ooc_window.muted_users:
                    option = int(dcd[7])
                    user.set_sprite_option(option)
                    self.sprite_window.set_subloc(user.get_subloc())
                    self.sprite_window.set_sprite(user)
                    col = self.user.color_ids[int(dcd[6])]
                    self.text_box.display_text(dcd[8], user, col, self.user.username)

            elif msg.identify() == 'char':
                dcd = msg.decode_other()
                self.update_char(*dcd)
            elif msg.identify() == 'OOC':
                dcd = msg.decode_other()
                self.ooc_window.update_ooc(*dcd)
            elif msg.identify() == 'music':
                dcd = msg.decode_other()
                if dcd[0] == "stop":
                    self.log_window.add_special_entry("{} stopped the music.\n".format(dcd[1]))
                    if config.getdefaultint('other', 'log_scrolling', 1):
                        self.log_window.scroll_y = 0
                    self.ooc_window.music_stop(False)
                else:
                    self.log_window.add_special_entry("{} changed the music.\n".format(dcd[1]))
                    if config.getdefaultint('other', 'log_scrolling', 1):
                        self.log_window.scroll_y = 0
                    self.ooc_window.on_music_play(dcd[0])

    def update_music(self, url):
        self.manager.irc_connection.send_special('music', url)

    def update_char(self, char, username):
        self.ooc_window.update_char(char, username)
        if username == self.user.username:
            return
        if char not in characters:
            self.users[username].set_char(characters['RedHerring'])
            self.users[username].set_current_sprite('4')
        else:
            self.users[username].set_char(characters[char])
        self.users[username].get_char().load(no_icons=True)

    def on_join(self, username):
        if username not in self.users:
            self.users[username] = User(username)
            self.ooc_window.add_user(self.users[username])
        self.log_window.add_special_entry("{} has joined.\n".format(username))
        config = App.get_running_app().config
        if config.getdefaultint('other', 'log_scrolling', 1):
            self.log_window.scroll_y = 0
        char = self.user.get_char()
        if char is not None:
            self.manager.irc_connection.send_special('char', char.name)

    def on_disconnect(self, username):
        self.log_window.add_special_entry("{} has disconnected.\n".format(username))
        config = App.get_running_app().config
        if config.getdefaultint('other', 'log_scrolling', 1):
            self.log_window.scroll_y = 0
        self.ooc_window.delete_user(username)
        try:
            self.users[username].remove()
            del self.users[username]
        except KeyError:
            pass

    def on_join_users(self, users):
        users = users.split()
        for u in users:
            if u == "@" + self.user.username:
                continue
            if u != self.user.username:
                self.users[u] = User(u)
                self.ooc_window.add_user(self.users[u])
