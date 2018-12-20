from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget


class UserBox(Widget):
    lbl = ObjectProperty(None)
    pm = ObjectProperty(None)
    mute = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(UserBox, self).__init__(**kwargs)
        self.popup = UserBoxPopup()
        self.char_lbl_text = ""
        self.sub_lbl_text = ""
        self.loc_lbl_text = ""

    def on_label_touch_down(self, inst, touch):
        if self.lbl.collide_point(*touch.pos):
            self.set_new_popup()
            self.popup.open()

    def set_new_popup(self):
        del self.popup
        size = len(self.char_lbl_text)
        if len(self.sub_lbl_text) > size:
            size = len(self.sub_lbl_text)
        if len(self.loc_lbl_text) > size:
            size = len(self.loc_lbl_text)
        self.popup = UserBoxPopup(size=[size*10+15, 100])
        self.popup.char_lbl.text = self.char_lbl_text
        self.popup.sub_lbl.text = self.sub_lbl_text
        self.popup.loc_lbl.text = self.loc_lbl_text

    def set_char_label(self, text):
        self.char_lbl_text = text

    def set_sub_label(self, text):
        self.sub_lbl_text = text

    def set_loc_label(self, text):
        self.loc_lbl_text = text


class UserBoxPopup(ModalView):
    char_lbl = ObjectProperty(None)
    sub_lbl = ObjectProperty(None)
    loc_lbl = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(UserBoxPopup, self).__init__(**kwargs)
        self.background_color = [0, 0, 0, 0]

