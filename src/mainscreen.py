from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.properties import ObjectProperty, StringProperty
from kivy.clock import Clock

from character import Character


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

    def __init__(self, **kwargs):
        super(SpritePreview, self).__init__(**kwargs)

    def set_sprite(self, sprite):
        self.texture = sprite


class SpriteWindow(Widget):

    center_sprite = ObjectProperty(None)
    left_sprite = ObjectProperty(None)
    right_sprite = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SpriteWindow, self).__init__(**kwargs)

    def set_sprite(self, sprite):
        self.center_sprite.texture = sprite
        self.center_sprite.opacity = 1


class TextBox(Widget):

    def __init__(self, **kwargs):
        super(TextBox, self).__init__(**kwargs)



class LogWindow(ScrollView):

    def __init__(self, **kwargs):
        super(LogWindow, self).__init__(**kwargs)


class OOCWindow(ScrollView):

    def __init__(self, **kwargs):
        super(OOCWindow, self).__init__(**kwargs)


class MainScreen(Screen):
    icons_layout = ObjectProperty(None)
    sprite_preview = ObjectProperty(None)
    sprite_window = ObjectProperty(None)
    msg_input = ObjectProperty(None)
    current_sprite = StringProperty("")

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.user = None

    def on_ready(self, *args):
        self.msg_input.bind(on_text_validate=self.send_message)
        Clock.schedule_once(self.refocus_text)
        self.user = App.get_running_app().get_user()
        char = self.user.get_char()
        if char is not None:
            self.icons_layout.load_icons(char.get_icons())

    def on_current_sprite(self, *args):
        char = self.user.get_char()
        sprite = char.get_sprite(self.current_sprite)
        self.sprite_preview.set_sprite(sprite)
        Clock.schedule_once(self.refocus_text, 0.5)

    def send_message(self, *args):
        self.msg_input.text = ""
        Clock.schedule_once(self.refocus_text)
        self.sprite_window.set_sprite(self.user.get_char().get_sprite(self.current_sprite))

    def refocus_text(self, *args):
        self.msg_input.focus = True

    def update_chat(self, dt):
        pass
