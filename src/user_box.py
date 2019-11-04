from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget

from src.mainscreen import MainScreen, RightClickMenu
from src.user import User, CurrentUserHandler


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
        self.popup = UserBoxPopup(size=[size * 10 + 15, 150])
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
    warp = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(UserBoxPopup, self).__init__(**kwargs)
        self.background_color = [0, 0, 0, 0]
        self.warp.bind(on_press=self.warp_pressed)

    def warp_pressed(self, value):
        main_scr: MainScreen = App.get_running_app().get_main_screen()
        user: User = App.get_running_app().get_user()
        user_handler: CurrentUserHandler = App.get_running_app().get_user_handler()

        from src.location import location_manager
        if not location_manager.has_location(self.loc_lbl.text):
            return

        try:
            if user.get_loc().get_name() != self.loc_lbl.text:
                RightClickMenu.on_loc_select(None, None, self.loc_lbl.text)
                main_scr.sprite_settings.update_sub(user.get_loc())
            if self.sub_lbl.text != "Missingno" and self.sub_lbl.text != "":
                main_scr.sprite_settings.on_subloc_select(None, self.sub_lbl.text)
        except KeyError as e:
            print(e)
            return
