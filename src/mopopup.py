from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class MOPopup(Popup):

    def __init__(self, title_, msg, btn_msg, **kwargs):
        self.content = BoxLayout(orientation='vertical')
        self.content.add_widget(Label(text=msg))
        btn = Button(text=btn_msg, size_hint=(1, 0.4))
        self.content.add_widget(btn)
        self.title = title_
        self.size_hint = (None, None)
        self.size = (400, 200)
        btn.bind(on_press=self.dismiss)
        super(MOPopup, self).__init__(**kwargs)
