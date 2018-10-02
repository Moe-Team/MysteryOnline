from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from character import characters, main_series_list
from math import ceil
from kivy.config import ConfigParser


class CharacterToggle(ToggleButton):

    def __init__(self, char, **kwargs):
        super(CharacterToggle, self).__init__(**kwargs)
        self.char = char
        self.name = char.name
        self.background_normal = self.char.avatar
        self.size_hint = (None, None)
        self.size = (60, 60)


class CharacterSelectSaved:

    def __init__(self, main_lay):
        self.main_lay = main_lay
        self.is_saved = False

    def save(self):
        self.is_saved = True

    def get_saved(self):
        return self.main_lay


class CharacterSelect(Popup):

    button_lay = ObjectProperty(None)
    scroll_lay = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CharacterSelect, self).__init__(**kwargs)
        self.picked_char = None
        self.main_lay = BoxLayout(orientation='vertical', size_hint=(1, None), height=self.height-100)
        self.scroll_lay.add_widget(self.main_lay)
        self.save = CharacterSelectSaved(self.main_lay)
        self.fill_with_chars()

    def on_size(self, *args):
        self.fill_with_chars()

    def fill_with_chars(self):
        self.scroll_lay.clear_widgets()
        if self.save.is_saved:
            main_lay = self.save.get_saved()
            self.scroll_lay.add_widget(main_lay)
            return

        grids = {}
        config = ConfigParser()
        config.read('mysteryonline.ini')
        favorites = config.get('other', 'fav_characters')
        favorites = list(filter(lambda x: x.name in favorites, characters.values()))
        mod = ceil(len(favorites) / 7)
        self.main_lay.add_widget(Label(text='Favorites', size_hint=(1, None), height=40))
        grids['Favorites'] = GridLayout(cols=7, size_hint=(1, None), height=60 * mod)
        self.main_lay.add_widget(grids['Favorites'])
        for s in sorted(main_series_list):
            self.create_series_rows(grids, s)

        for g in grids:
            self.fill_rows_with_chars(g, grids)

        ok_btn = Button(text="OK", size_hint=(1, None), height=40, pos_hint={'y': 0, 'x': 0})
        ok_btn.bind(on_release=self.dismiss)
        self.button_lay.add_widget(ok_btn)
        self.main_lay.bind(minimum_height=self.main_lay.setter('height'))
        self.save.save()
        self.scroll_lay.add_widget(self.main_lay)

    def fill_rows_with_chars(self, g, grids):
        config = ConfigParser()
        config.read('mysteryonline.ini')
        favorites = config.get('other', 'fav_characters')
        chars = list(filter(lambda x: x.series == g, characters.values()))
        chars = sorted(chars, key=lambda x: x.name)
        for c in chars:
                btn = CharacterToggle(c, group='char')
                btn.bind(on_touch_down=self.character_chosen)
                if c.name in favorites:
                    fav_btn = CharacterToggle(c, group='char')
                    fav_btn.bind(on_touch_down=self.character_chosen)
                    grids['Favorites'].add_widget(fav_btn)
                grids[g].add_widget(btn)

    def create_series_rows(self, grids, s):
        temp = list(filter(lambda x: x.series == s, characters.values()))
        mod = ceil(len(temp) / 7)
        self.main_lay.add_widget(Label(text=s, size_hint=(1, None), height=40))
        grids[s] = GridLayout(cols=7, size_hint=(1, None), height=60 * mod)
        self.main_lay.add_widget(grids[s])

    def character_chosen(self, inst, touch):
        if touch.button == 'right':
            try:
                if inst.collide_point(touch.x, touch.y):
                    favorite = App.get_running_app().get_fav_chars()
                    favorite.options = characters
                    for option in favorite.options:
                        state = 'down' if option in favorite.value else 'normal'
                        btn = ToggleButton(text=option, state=state, size_hint_y=None, height=50)
                        favorite.buttons.append(btn)
                    for btn in favorite.buttons:
                        if btn.text == characters[inst.name].name:
                            if btn.state == 'normal':
                                btn.state = 'down'
                            else:
                                btn.state = 'normal'
                            favorite.value = [btn.text for btn in favorite.buttons if btn.state == 'down']
                            favorite.buttons.clear()

                            self.save.is_saved = False
                            self.main_lay.clear_widgets()
                            self.fill_with_chars()
            except AttributeError:
                pass

        else:
            self.picked_char = inst.char

    def dismiss(self, inst):
        super(CharacterSelect, self).dismiss(animation=False)
