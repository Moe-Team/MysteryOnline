import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown


class Toolbar(BoxLayout):
    def __init__(self, **kwargs):
        super(Toolbar, self).__init__(**kwargs)
        self.user = None
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

        self.sfx_main_btn = Button(text='SFX')
        self.sfx_dropdown = None    
        self.sfx_name = None        
        self.sfx_list = []          
        self.load_sfx()
        self.add_widget(self.sfx_main_btn)

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

    def get_sfx_name(self):     
        if self.sfx_name == "None":
            self.sfx_name = None
        current_sfx = self.sfx_name
        if self.sfx_name is not None:
            self.sfx_main_btn.text = "None"
            self.sfx_name = None
        return current_sfx

    def load_sfx(self):         
        for file in os.listdir('sounds/sfx'):
            if file.endswith('wav'):
                self.sfx_list.append(file)

    def create_sfx_dropdown(self):
        self.sfx_dropdown = DropDown()
        fav_sfx = App.get_running_app().get_fav_sfx()
        btn = Button(text="None", size_hint_y=None, height=40)
        btn.bind(on_release=lambda x: self.sfx_dropdown.select(x.text))
        self.sfx_dropdown.add_widget(btn)
        for sfx in fav_sfx.value:
            if sfx in self.sfx_list:
                btn = Button(text=sfx, size_hint_y=None, height=40,
                             background_normal='atlas://data/images/defaulttheme/button_pressed',
                             background_down='atlas://data/images/defaulttheme/button')
                btn.bind(on_release=lambda x: self.sfx_dropdown.select(x.text))
                self.sfx_dropdown.add_widget(btn)
        for sfx in self.sfx_list:
            if sfx not in fav_sfx.value:
                btn = Button(text=sfx, size_hint_y=None, height=40)
                btn.bind(on_release=lambda x: self.sfx_dropdown.select(x.text))
                self.sfx_dropdown.add_widget(btn)

        btn = Button(text="None", size_hint_y=None, height=40)
        btn.bind(on_release=lambda x: self.sfx_dropdown.select(x.text))
        self.sfx_main_btn.bind(on_release=self.sfx_dropdown.open)
        self.sfx_dropdown.add_widget(btn)
        self.sfx_dropdown.bind(on_select=lambda instance, x: setattr(self.sfx_main_btn, 'text', x))
        self.sfx_dropdown.bind(on_select=lambda instance, x: setattr(self, 'sfx_name', x))
        self.sfx_dropdown.bind(on_dismiss=self.refocus_screen)

    def refocus_screen(self, inst):
        main_scr = App.get_running_app().get_main_screen()
        main_scr.refocus_text()
