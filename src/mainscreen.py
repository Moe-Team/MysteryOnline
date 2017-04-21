from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
from kivy.uix.dropdown import DropDown
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock

from character import Character
from location import locations


class Toolbar(BoxLayout):

    def __init__(self, **kwargs):
        super(Toolbar, self).__init__(**kwargs)
        self.subloc_drop = DropDown(size_hint=(None, None), size=(400, 40))
        self.pos_drop = DropDown(size_hint=(None, None), size=(400, 40))
        for pos in ('center', 'right', 'left'):
            btn = Button(text=pos, size_hint=(None, None), size=(400, 40))
            btn.bind(on_release=lambda btn: self.pos_drop.select(btn.text))
            self.pos_drop.add_widget(btn)

        self.pos_btn = Button(size_hint=(None, None), size=(400, 40))
        self.pos_btn.text = 'center'
        self.pos_btn.bind(on_release=self.pos_drop.open)
        self.add_widget(self.pos_btn)
        self.pos_drop.bind(on_select=self.on_pos_select)

    def update_sub(self, loc):
        for sub in loc.list_sub():
            btn = Button(text=sub, size_hint=(None, None), size=(400, 40))
            btn.bind(on_release=lambda btn: self.subloc_drop.select(btn.text))
            self.subloc_drop.add_widget(btn)

        self.main_btn = Button(size_hint=(None, None), size=(400, 40))
        self.main_btn.text = loc.get_first_sub()
        self.main_btn.bind(on_release=self.subloc_drop.open)
        self.add_widget(self.main_btn)
        self.subloc_drop.bind(on_select=self.on_subloc_select)

    def on_subloc_select(self, inst, subloc):
        self.main_btn.text = subloc
        main_scr = self.parent.parent # Always blame Kivy
        main_scr.current_subloc = subloc

    def on_pos_select(self, inst, pos):
        self.pos_btn.text = pos
        main_scr = self.parent.parent # I will never forgive Kivy
        main_scr.current_pos = pos


class Icon(Image):

    def __init__(self, name, ic, **kwargs):
        super(Icon, self).__init__(**kwargs)
        self.texture = ic
        self.name = name
        self.size_hint = (None, None)
        self.size = (40, 40)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.sprite_picked(self, self.name)
            return True

class IconsLayout(GridLayout):

    def __init__(self, **kwargs):
        super(IconsLayout, self).__init__(**kwargs)
        self.cols = 5
        self.current_icon = None

    def load_icons(self, icons):
        for i in sorted(icons.textures.keys()):
            self.add_widget(Icon(i, icons[i]))
        self.sprite_picked(self.children[-1], "1")

    def sprite_picked(self, icon, sprite_name):
        main_scr = self.parent.parent # blame kivy
        main_scr.current_sprite = sprite_name
        if self.current_icon is not None:
            self.current_icon.color = [1, 1, 1, 1]
        icon.color = [0.3, 0.3, 0.3, 1]
        self.current_icon = icon


class SpritePreview(Image):

    center_sprite = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SpritePreview, self).__init__(**kwargs)

    def set_subloc(self, sub):
        self.texture = sub.get_img().texture

    def set_sprite(self, sprite):
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
            subloc.set_r_user(user)
        elif pos == 'left':
            subloc.set_l_user(user)
        else:
            subloc.set_c_user(user)

        self.display_sub(subloc)

    def set_subloc(self, subloc):
        self.background.texture = subloc.get_img().texture

    def display_sub(self, subloc):
        if subloc.get_c_user() is not None:
            sprite = subloc.get_c_user().get_char().get_current_sprite()
            self.center_sprite.texture = sprite
            self.center_sprite.opacity = 1
            self.center_sprite.size = self.center_sprite.texture.size
        else:
            self.center_sprite.texture = None
            self.center_sprite.opacity = 0

        if subloc.get_l_user() is not None:
            sprite = subloc.get_l_user().get_char().get_current_sprite()
            self.left_sprite.texture = sprite
            self.left_sprite.opacity = 1
            self.left_sprite.size = self.left_sprite.texture.size
        else:
            self.left_sprite.texture = None
            self.left_sprite.opacity = 0

        if subloc.get_r_user() is not None:
            sprite = subloc.get_r_user().get_char().get_current_sprite()
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

    def display_text(self, msg, user):
        if self.prev_user is not user:
            self.text = ""
        self.prev_user = user
        char_name = user.get_char().name
        self.char_name.text = char_name
        self.msg = msg

        def text_gen(text):
            for c in text:
                yield c

        self.gen = text_gen(self.msg)
        Clock.schedule_interval(self._animate, 1.0/60.0)

    def _animate(self, dt):
        try:
            self.text += next(self.gen)
        except StopIteration:
            self.text += " "
            return False


class LogWindow(ScrollView):

    def __init__(self, **kwargs):
        super(LogWindow, self).__init__(**kwargs)


class OOCWindow(ScrollView):

    def __init__(self, **kwargs):
        super(OOCWindow, self).__init__(**kwargs)


class RightClickMenu(ModalView):

    def __init__(self, **kwargs):
        super(RightClickMenu, self).__init__(**kwargs)


class MainScreen(Screen):

    icons_layout = ObjectProperty(None)
    sprite_preview = ObjectProperty(None)
    sprite_window = ObjectProperty(None)
    msg_input = ObjectProperty(None)
    toolbar = ObjectProperty(None)
    text_box = ObjectProperty(None)

    current_sprite = StringProperty("")
    current_loc = ObjectProperty(None)
    current_subloc = StringProperty("")
    current_pos = StringProperty("center")

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.user = None

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
        # Called when main screen becomes active
        self.msg_input.bind(on_text_validate=self.send_message)
        Clock.schedule_once(self.refocus_text)

        self.user = App.get_running_app().get_user()
        self.current_loc = locations['Hakuryou']
        char = self.user.get_char()
        if char is not None:
            self.icons_layout.load_icons(char.get_icons())

    def on_current_loc(self, *args):
        # Called when the current location changes
        self.user.set_loc(self.current_loc)
        subloc = locations['Hakuryou'].get_first_sub()
        self.current_subloc = subloc
        self.toolbar.update_sub(self.current_loc)

    def on_current_subloc(self, *args):
        # Called when the current sublocation changes
        subloc = self.current_loc.get_sub(self.current_subloc)
        self.user.set_subloc(subloc)
        self.sprite_preview.set_subloc(subloc)

    def on_current_pos(self, *args):
        self.user.set_pos(self.current_pos)

    def on_current_sprite(self, *args):
        # Called when user picks new sprite
        char = self.user.get_char()
        char.set_current_sprite(self.current_sprite)
        sprite = char.get_current_sprite()
        self.sprite_preview.set_sprite(sprite)
        Clock.schedule_once(self.refocus_text, 0.1)

    def send_message(self, *args):
        Clock.schedule_once(self.refocus_text)
        sprite = self.user.get_char().get_sprite(self.current_sprite)
        self.sprite_window.set_sprite(self.user)
        subloc = self.current_loc.get_sub(self.current_subloc)
        self.sprite_window.set_subloc(subloc)

        msg = self.msg_input.text
        self.msg_input.text = ""
        self.text_box.display_text(msg, self.user)

    def refocus_text(self, *args):
        # Refocusing the text input has to be done this way cause Kivy
        self.msg_input.focus = True

    def update_chat(self, dt):
        pass
