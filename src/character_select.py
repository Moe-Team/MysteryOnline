from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.graphics import Color, Rectangle
from character import characters, series_list
from math import ceil


class CharacterToggle(ToggleButton):

    def __init__(self, char, **kwargs):
        super(CharacterToggle, self).__init__(**kwargs)
        self.char = char
        self.background_normal = self.char.avatar
        self.size_hint = (None, None)
        self.size = (60, 60)


class CharacterSelect(Popup):

    main_lay = ObjectProperty(None)
    button_lay = ObjectProperty(None)
    scroll_lay = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CharacterSelect, self).__init__(**kwargs)
        self.title = "Select your character"
        self.size_hint = (0.7, 0.7)
        self.auto_dismiss = False
        self.picked_char = None
        grids = {}
        for s in series_list:
            self.main_lay.add_widget(Label(text=s, size_hint=(1.2, None)))
            grids[s] = GridLayout(cols=7, size_hint=(1, None))
            self.main_lay.add_widget(grids[s])

        for g in grids:
            chars = list(filter(lambda x: x.series == g, characters.values()))
            chars = sorted(chars, key=lambda x: x.name)
            for c in chars:
                btn = CharacterToggle(c, group='char', size_hint=(1, None), height=60)
                btn.bind(on_press=self.character_chosen)
                grids[g].add_widget(btn)
        ok_btn = Button(text="OK", size_hint=(1, None), height=40, pos_hint={'y': 0, 'x': 0})
        ok_btn.bind(on_press=self.dismiss)
        self.button_lay.add_widget(ok_btn)
        self.main_lay.bind(minimum_height=self.main_lay.setter('height'))

    def character_chosen(self, inst):
        self.picked_char = inst.char
