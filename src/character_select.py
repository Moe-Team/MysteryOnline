from kivy.uix.popup import Popup
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
        grids = {}
        for s in series:
            self.main_lay.add_widget(Label(text=s, size_hint=(0.1, 0.1)))
            grids[s] = GridLayout(cols=7)
            self.main_lay.add_widget(grids[s])

        for g in grids:
            chars = list(filter(lambda x: x.series == g, characters.values()))
            for c in chars:
                grids[g].add_widget(CharacterToggle(c))
