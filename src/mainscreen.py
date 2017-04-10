from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.properties import ObjectProperty
from kivy.clock import Clock

from character import Character


class SpriteWindow(Widget):

    center_sprite = ObjectProperty(None)
    left_sprite = ObjectProperty(None)
    right_sprite = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SpriteWindow, self).__init__(**kwargs)


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
    msg_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.user = None

    def on_ready(self, *args):
        pass

    def update_chat(self, dt):
        pass
