from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from character import characters, series


class CharacterToggle(ToggleButton):

    def __init__(self, char, **kwargs):
        super(CharacterToggle, self).__init__(**kwargs)
        self.char = char
        self.background_normal = self.char.avatar
        self.size_hint = (None, None)
        self.size = (60, 60)


class CharacterSelect(Popup):

    main_lay = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CharacterSelect, self).__init__(**kwargs)
        self.title = "Select your character"
        self.size_hint = (0.7, 0.7)
        self.auto_dismiss = False
        self.picked_char = None
        grids = {}
        for s in series:
            self.main_lay.add_widget(Label(text=s, size_hint=(0.1, 0.1)))
            grids[s] = GridLayout(cols=7)
            self.main_lay.add_widget(grids[s])

        for g in grids:
            chars = list(filter(lambda x: x.series == g, characters.values()))
            for c in chars:
                btn = CharacterToggle(c, group='char')
                btn.bind(on_press=self.character_chosen)
                grids[g].add_widget(btn)
        ok_btn = Button(text="OK", size_hint=(0.1, 0.1))
        ok_btn.bind(on_press=self.dismiss)
        self.main_lay.add_widget(ok_btn)

    def character_chosen(self, inst):
        self.picked_char = inst.char
