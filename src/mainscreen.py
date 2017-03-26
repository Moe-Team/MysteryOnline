from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty


class MainScreen(Screen):
    msg_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

    def update_chat(self, dt):
        pass
