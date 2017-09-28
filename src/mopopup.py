from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class MOPopup(Popup):

    def __init__(self, title_, msg, btn_msg, dismissable=True, *args, **kwargs):
        self.box_lay = BoxLayout(orientation='vertical')
        self.content = self.box_lay
        self.content.add_widget(Label(text=msg))
        if dismissable:
            btn = Button(text=btn_msg, size_hint=(1, 0.4))
            self.content.add_widget(btn)
            btn.bind(on_press=self.dismiss)
        else:
            self.auto_dismiss = False
        self.title = title_
        self.size_hint = (None, None)
        self.size = (400, 200)
        super(MOPopup, self).__init__(**kwargs)
