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
            self.parent.sprite_picked(self.name)

class IconsLayout(GridLayout):

    def __init__(self, **kwargs):
        super(IconsLayout, self).__init__(**kwargs)
        self.cols = 5

    def load_icons(self, icons):
        for i in sorted(icons.textures.keys()):
            self.add_widget(Icon(i, icons[i]))

    def sprite_picked(self, sprite_name):
        main_scr = self.parent.parent # blame kivy
        main_scr.current_sprite = sprite_name


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
        pass


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
    current_sprite = StringProperty("")

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.user = None

    def on_ready(self, *args):
        self.user = App.get_running_app().get_user()
        char = self.user.get_char()
        if char is not None:
            self.icons_layout.load_icons(char.get_icons())

    def on_current_sprite(self, *args):
        char = self.user.get_char()
        self.sprite_preview.set_sprite(char.get_sprite(self.current_sprite))

    def update_chat(self, dt):
        pass
