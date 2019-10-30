from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.config import ConfigParser
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from character import characters, main_series_list
from math import ceil
from utils import binary_search


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
    search_bar = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(CharacterSelect, self).__init__(**kwargs)
        self.picked_char = None
        self.main_lay = BoxLayout(orientation='vertical', size_hint=(1, None), height=self.height-100)
        self.scroll_lay.add_widget(self.main_lay)
        self.save = CharacterSelectSaved(self.main_lay)
        self.value = []
        chars = list(characters.values())
        self.chars = {x.name.lower(): x for x in chars}
        self.search_space = sorted(self.chars.keys())
        self.search_results = []
        self.search_done = False
        self.search_button = None
        self.ready()
        self.fill_with_chars()

    def ready(self):
        self.search_bar.focus = True

    def on_size(self, *args):
        self.fill_with_chars()

    def fill_with_chars(self):
        self.scroll_lay.clear_widgets()
        if self.save.is_saved:
            main_lay = self.save.get_saved()
            self.scroll_lay.add_widget(main_lay)
            return

        grids = {}
        fav = App.get_running_app().get_fav_chars()
        favorites = list(filter(lambda x: x.name in fav.value, characters.values()))
        mod = ceil(len(favorites) / 7)
        fav_button = ToggleButton(text='Favorites', size_hint=(1, None), height=25)
        if fav_button.text in self.value:
            fav_button.state = 'down'
        fav_button.bind(state=self.series_dropdown)
        self.main_lay.add_widget(fav_button)
        if fav_button.state is 'down':
            grids['Favorites'] = GridLayout(cols=7, size_hint=(1, None), height=60 * mod)
            self.main_lay.add_widget(grids['Favorites'])

        mod = ceil(len(self.search_results) / 7)
        self.search_button = ToggleButton(text='Search', size_hint=(1, None), height=25)
        if self.search_button.text in self.value:
            self.search_button.state = 'down'
        self.search_button.bind(state=self.series_dropdown)
        self.main_lay.add_widget(self.search_button)
        if self.search_button.state is 'down':
            grids['Search'] = GridLayout(cols=7, size_hint=(1, None), height=60 * mod)
            self.main_lay.add_widget(grids['Search'])

        for s in sorted(main_series_list):
            self.create_series_rows(grids, s)

        for g in grids:
            self.fill_rows_with_chars(g, grids)
        self.main_lay.bind(minimum_height=self.main_lay.setter('height'))
        self.save.save()
        self.scroll_lay.add_widget(self.main_lay)

    def fill_rows_with_chars(self, g, grids):
        chars = list(filter(lambda x: x.series == g, characters.values()))
        chars = sorted(chars, key=lambda x: x.name)
        fav = App.get_running_app().get_fav_chars()
        config = ConfigParser()
        config.read('mysteryonline.ini')
        fav_list = str(config.get('other', 'fav_characters').strip('[]'))
        fav_list = fav_list.replace("'", "")
        fav_list = fav_list.split(',')
        fav_list = [x.strip() for x in fav_list]

        if g == 'Search':
            for char_name in self.search_results:
                found_char = self.chars[char_name]
                btn = CharacterToggle(found_char, group='char', size=[60, 60], text_size=[60, 60], valign='center',
                                      halign='center', markup=True)
                btn.bind(on_touch_down=self.right_click, state=self.character_chosen)
                if char_name == self.picked_char:
                    btn.state = 'down'
                grids[g].add_widget(btn)

        for c in chars:
            if c.name in fav_list and c.name in fav.value and 'Favorites' in self.value:
                fav_btn = CharacterToggle(c, group='char', size=[60, 60], text_size=[60, 60], valign='center',
                                          halign='center', markup=True)
                fav_btn.bind(on_touch_down=self.right_click, state=self.character_chosen)
                if c == self.picked_char:
                    fav_btn.state = 'down'
                grids['Favorites'].add_widget(fav_btn)
            if c.series in self.value:
                btn = CharacterToggle(c, group='char', size=[60, 60], text_size=[60, 60], valign='center',
                                      halign='center', markup=True)
                btn.bind(on_touch_down=self.right_click, state=self.character_chosen)
                if c == self.picked_char:
                    btn.state = 'down'
                grids[g].add_widget(btn)
        fav_list.clear()

    def character_chosen(self, inst, value):
        if value is 'down':
            inst.text = '[size=9]'+inst.name+'[/size]'
            self.picked_char = None
            self.picked_char = inst.char
        else:
            inst.text = ''
            if self.picked_char == inst.char:
                self.picked_char = None

    def create_series_rows(self, grids, s):
        temp = list(filter(lambda x: x.series == s, characters.values()))
        mod = ceil(len(temp) / 7)
        series = ToggleButton(text=s, size_hint=(1, None), height=25)
        if series.text in self.value:
            series.state = 'down'
        series.bind(state=self.series_dropdown)
        self.main_lay.add_widget(series)
        if series.state is 'down':
            grids[s] = GridLayout(cols=7, size_hint=(1, None), height=60 * mod)
        else:
            grids[s] = GridLayout(cols=7, size_hint=(1, None), height=0)
        self.main_lay.add_widget(grids[s])

    def series_dropdown(self, instance, value):
        if value is 'down':
            self.value.append(instance.text)
        else:
            try:
                self.value.remove(instance.text)
            except ValueError:
                pass
        self.save.is_saved = False
        self.main_lay.clear_widgets()
        self.fill_with_chars()

    def right_click(self, inst, touch):
        if touch.button == 'right':
            try:
                if inst.collide_point(touch.x, touch.y):
                    favorite = App.get_running_app().get_fav_chars()
                    favorite.options = characters
                    config = ConfigParser()
                    config.read('mysteryonline.ini')
                    fav_list = str(config.get('other', 'fav_characters').strip('[]'))
                    fav_list = fav_list.replace("'", "")
                    fav_list = fav_list.split(',')
                    fav_list = [x.strip() for x in fav_list]
                    for option in favorite.options:
                        state = 'down' if option in favorite.value and option in fav_list else 'normal'
                        btn = ToggleButton(text=option, state=state, size_hint_y=None, height=50)
                        favorite.buttons.append(btn)
                    for btn in favorite.buttons:
                        if btn.text is characters[inst.name].name:
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

    def search(self, target):
        if target == "":
            self.clear_search()
            return
        if self.search_done:
            self.clear_search()
        self.search_bar.text = ""
        Clock.schedule_once(self.refocus)
        self.search_button.state = 'down'
        self.search_results = self.find_char(target)
        self.save.is_saved = False
        self.main_lay.clear_widgets()
        self.fill_with_chars()

    def find_char(self, target):
        found_index = binary_search(self.search_space, target)
        if found_index is None:
            return []
        self.search_done = True
        i = found_index
        current_char = self.search_space[i].lower()
        result = []
        while current_char.startswith(target.lower()):
            result.append(current_char)
            if i == len(self.search_space) - 1:
                break
            i += 1
            current_char = self.search_space[i].lower()
        i = found_index
        if i > 0:
            i -= 1
            current_char = self.search_space[i].lower()
            while current_char.startswith(target.lower()):
                result.append(current_char)
                if i == 0:
                    break
                i -= 1
                current_char = self.search_space[i].lower()
        return result

    def clear_search(self):
        if not self.search_done:
            return
        self.search_done = False
        self.search_results = []
        self.search_button.state = 'normal'
        self.save.is_saved = False
        self.main_lay.clear_widgets()
        self.fill_with_chars()

    def refocus(self, *args):
        self.search_bar.focus = True

    def dismiss(self, inst):
        user = App.get_running_app().get_user()
        if self.picked_char and user is not None:
            print(self.picked_char)
            user.set_char(self.picked_char)
            user.get_char().load()
            main_scr = App.get_running_app().get_main_screen()
            main_scr.on_new_char(user.get_char())
        super(CharacterSelect, self).dismiss(animation=False)
