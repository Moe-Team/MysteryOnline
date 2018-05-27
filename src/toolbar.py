from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown

from location import location_manager


class Toolbar(BoxLayout):
    def __init__(self, **kwargs):
        super(Toolbar, self).__init__(**kwargs)
        self.user = None
        self.main_btn = None
        self.subloc_drop = DropDown(size_hint=(None, None), size=(200, 30))
        self.color_drop = DropDown(size_hint=(None, None), size=(100, 30))
        for col in ('red', 'blue', 'golden', 'green', 'rainbow', 'purple', 'normal'):
            btn = Button(text=col, size_hint=(None, None), size=(100, 30))
            btn.bind(on_release=lambda btn_: self.color_drop.select(btn_.text))
            self.color_drop.add_widget(btn)
        self.text_col_btn = Button(text='color', size_hint=(None, None), size=(100, 30))
        self.text_col_btn.bind(on_release=self.color_drop.open)
        self.add_widget(self.text_col_btn)
        self.color_drop.bind(on_select=self.on_col_select)
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

    def on_subloc_select(self, inst, subloc_name):
        self.main_btn.text = subloc_name
        main_scr = App.get_running_app().get_main_screen()
        user_handler = App.get_running_app().get_user_handler()
        user_handler.set_current_subloc_name(subloc_name)
        sub = user_handler.get_current_subloc()
        main_scr.sprite_preview.set_subloc(sub)
        main_scr.refocus_text()

    def on_col_select(self, inst, col, user=None):
        main_scr = App.get_running_app().get_main_screen()
        if user is None:
            user = main_scr.user
        user.on_col_select(col, self.text_col_btn)
        main_scr.refocus_text()

    def on_item_select(self, inst, item):
        self.text_item_btn.text = item
        if item != "no item":
            item = self.user.inventory.get_item_by_name(item)
            self.user.inventory.send_item(item)
        self.text_item_btn.text = "no item"
