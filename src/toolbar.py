from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.image import Image

from location import locations


class Toolbar(BoxLayout):
    def __init__(self, **kwargs):
        super(Toolbar, self).__init__(**kwargs)
        self.user = None
        self.main_btn = None
        self.main_loc_btn = None
        self.subloc_drop = DropDown(size_hint=(None, None), size=(200, 30))
        self.pos_drop = DropDown(size_hint=(None, None), size=(100, 30))
        for pos in ('center', 'right', 'left'):
            btn = Button(text=pos, size_hint=(None, None), size=(100, 30))
            btn.bind(on_release=lambda btn_: self.pos_drop.select(btn_.text))
            self.pos_drop.add_widget(btn)
        self.color_drop = DropDown(size_hint=(None, None), size=(200, 30))
        for col in ('red', 'blue', 'golden', 'green', 'rainbow', 'normal'):
            btn = Button(text=col, size_hint=(None, None), size=(200, 30))
            btn.bind(on_release=lambda btn_: self.color_drop.select(btn_.text))
            self.color_drop.add_widget(btn)
        self.text_col_btn = Button(text='color', size_hint=(None, None), size=(200, 30))
        self.text_col_btn.bind(on_release=self.color_drop.open)
        self.add_widget(self.text_col_btn)
        self.color_drop.bind(on_select=self.on_col_select)
        self.pos_btn = Button(size_hint=(None, None), size=(100, 30))
        self.pos_btn.text = 'center'
        self.pos_btn.bind(on_release=self.pos_drop.open)
        self.add_widget(self.pos_btn)
        self.pos_drop.bind(on_select=self.on_pos_select)
        self.loc_drop = DropDown(size_hint=(None, None), size=(200, 30))
        self.item_drop = DropDown(size_hint=(None, None), size=(200, 30))
        self.text_item_btn = Button(text='no item', size_hint=(None, None), size=(200, 30))
        self.text_item_btn.bind(on_release=self.build_item_drop)
        self.text_item_btn.bind(on_release=self.item_drop.open)
        self.add_widget(self.text_item_btn)
        self.item_drop.bind(on_select=self.on_item_select)

    def build_item_drop(self, pos):
        self.item_drop.clear_widgets()
        item_list = self.user.inventory.get_item_string_list()
        default_btn = Button(text="no item", size_hint=(None, None), size=(200, 30))
        default_btn.bind(on_release=lambda btn_: self.item_drop.select(btn_.text))
        self.item_drop.add_widget(default_btn)
        for item in item_list:
            btn = Button(text=item, size_hint=(None, None), size=(200, 30))
            btn.bind(on_release=lambda btn_: self.item_drop.select(btn_.text))
            self.item_drop.add_widget(btn)

    def set_user(self, user):
        self.user = user

    def update_sub(self, loc):
        if self.main_btn is not None:
            self.subloc_drop.clear_widgets()
        for sub in loc.list_sub():
            btn = Button(text=sub, size_hint=(None, None), size=(200, 30))
            btn.bind(on_release=lambda btn_: self.subloc_drop.select(btn_.text))
            self.subloc_drop.add_widget(btn)
        if self.main_btn is None:
            self.main_btn = Button(size_hint=(None, None), size=(200, 30))
            self.main_btn.bind(on_release=self.subloc_drop.open)
            self.add_widget(self.main_btn)
            self.subloc_drop.bind(on_select=self.on_subloc_select)
        self.main_btn.text = loc.get_first_sub()

    def update_loc(self):
        for l in locations:
            btn = Button(text=l, size_hint=(None, None), size=(200, 30))
            btn.bind(on_release=lambda btn_: self.loc_drop.select(btn_.text))
            self.loc_drop.add_widget(btn)
        self.main_loc_btn = Button(size_hint=(None, None), size=(200, 30))
        user_handler = App.get_running_app().get_user_handler()
        current_loc = user_handler.get_current_loc()
        self.main_loc_btn.text = current_loc.name
        self.main_loc_btn.bind(on_release=self.loc_drop.open)
        self.add_widget(self.main_loc_btn)
        self.loc_drop.bind(on_select=self.on_loc_select)

    def on_loc_select(self, inst, loc_name):
        self.main_loc_btn.text = loc_name
        main_scr = App.get_running_app().get_main_screen()
        user_handler = App.get_running_app().get_user_handler()
        loc = locations[loc_name]
        user_handler.set_current_loc(loc)
        self.update_sub(loc)
        main_scr.sprite_preview.set_subloc(user_handler.get_current_subloc())

    def on_subloc_select(self, inst, subloc_name):
        self.main_btn.text = subloc_name
        main_scr = App.get_running_app().get_main_screen()
        user_handler = App.get_running_app().get_user_handler()
        user_handler.set_current_subloc_name(subloc_name)
        sub = user_handler.get_current_subloc()
        main_scr.sprite_preview.set_subloc(sub)
        main_scr.refocus_text()

    def on_pos_select(self, inst, pos):
        self.pos_btn.text = pos
        main_scr = App.get_running_app().get_main_screen()
        user_handler = App.get_running_app().get_user_handler()
        user_handler.set_current_pos_name(pos)
        main_scr.refocus_text()

    def on_col_select(self, inst, col, user=None):
        self.text_col_btn.text = col
        main_scr = App.get_running_app().get_main_screen()
        if user is None:
            user = main_scr.user
        user.set_color(col)
        if user.color != 'ffffff':
            user.colored = True
        else:
            user.colored = False
        main_scr.refocus_text()

    def on_item_select(self, inst, item):
        self.text_item_btn.text = item
        if item != "no item":
            item = self.user.inventory.get_item_by_name(item)
            popup = item.build_item_window()
            popup.open()

