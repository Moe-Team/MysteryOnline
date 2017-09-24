from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView
from kivy.uix.widget import Widget


class TooltipBehavior(Widget):
    def __init__(self, **kwargs):
        super(TooltipBehavior, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
        self.popup = None

    def on_mouse_pos(self, *args):
        if not self.parent or not self.parent.parent:
            return
        if not self.get_root_window():
            return
        pos = args[1]
        Clock.unschedule(self.display_tooltip)  # cancel scheduled event since I moved the cursor
        self.close_tooltip()  # close if it's opened
        if self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.display_tooltip, 0.4)

    def display_tooltip(self, *args):
        if not self.parent or not self.parent.parent:
            return
        if len(Window.children) > 1:
            return
        self.set_new_popup()
        self.reposition()
        self.popup.open()

    def close_tooltip(self, *args):
        if not self.parent or not self.parent.parent:
            return
        self.popup.dismiss()

    def reposition(self):
        x, y = self.to_window(self.x, self.y)
        menu_x = x / Window.width
        menu_y = y / Window.height
        if y >= self.popup.height:
            loc_y = 'top'
        else:
            loc_y = 'y'
        self.popup.pos_hint = {'x': menu_x, loc_y: menu_y}

    def set_new_popup(self):
        pass


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
