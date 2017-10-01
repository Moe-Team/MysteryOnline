from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView

from tooltip import TooltipBehavior


class UserBox(TooltipBehavior):
    lbl = ObjectProperty(None)
    pm = ObjectProperty(None)
    mute = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(UserBox, self).__init__(**kwargs)
        self.popup = UserBoxPopup()
        self.char_lbl_text = ""
        self.sub_lbl_text = ""
        self.loc_lbl_text = ""

    def set_new_popup(self):
        self.popup = UserBoxPopup()
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
