from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty


class SpriteWindow(Widget):

    def __init__(self, **kwargs):
        super(SpriteWindow, self).__init__(**kwargs)


class LogWindow(ScrollView):

    def __init__(self, **kwargs):
        super(LogWindow, self).__init__(**kwargs)


class MainScreen(Screen):
    msg_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

    def update_chat(self, dt):
        pass
