from kivy.uix.settings import SettingItem
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.metrics import dp
from kivy.app import App
from character import main_series_list, extra_series_list, characters


class ScrollablePopup(Popup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class MultiChoiceOptions(SettingItem):

    options = ListProperty()
    buttons = ListProperty()
    popup = ObjectProperty(None, allownone=True)

    def on_panel(self, instance, value):
        if value is None:
            return
        self.fbind('on_release', self._create_popup)

    def _set_options(self, instance):
        self.value = [btn.text for btn in self.buttons if btn.state == 'down']
        self._dismiss()

    def _dismiss(self, *args):
        self.buttons.clear()
        self.popup.dismiss()

    def _create_popup(self, instance):
        self._create_options()
        content = BoxLayout(orientation='vertical', spacing='5dp', size_hint_y=None, height=500)
        content.bind(minimum_height=content.setter('height'))
        self.popup = popup = ScrollablePopup()

        for option in self.options:
            state = 'down' if option in self.value else 'normal'
            btn = ToggleButton(text=option, state=state, size_hint_y=None, height=50)
            self.buttons.append(btn)
            content.add_widget(btn)

        popup.scroll_lay.add_widget(content)

        box = BoxLayout(size_hint_y=None, height=dp(50), pos_hint={'y': 0, 'x': 0})
        popup.button_lay.add_widget(box)

        btn = Button(text='Done', size_hint_y=None, height=dp(50))
        btn.bind(on_release=self._set_options)
        box.add_widget(btn)

        btn = Button(text='Cancel', size_hint_y=None, height=dp(50))
        btn.bind(on_release=self._dismiss)
        box.add_widget(btn)

        popup.open()

    def _create_options(self):
        pass


class SeriesWhitelist(MultiChoiceOptions):

    def _create_options(self):
        self.options = main_series_list[:]
        self.options.extend(extra_series_list[:])


class FavCharacterList(MultiChoiceOptions):

    def __init__(self, **kwargs):
        super(SettingItem, self).__init__(**kwargs)
        self.value = self.panel.get_value(self.section, self.key)
        App.get_running_app().set_fav_chars(self)

    def _create_options(self):
        self.options = characters
        App.get_running_app().set_fav_chars(self)


class FavSFXList(MultiChoiceOptions):

    def __init__(self, **kwargs):
        super(SettingItem, self).__init__(**kwargs)
        self.value = self.panel.get_value(self.section, self.key)
        self._create_options()
        for option in self.options:
            state = 'down' if option in self.value else 'normal'
            btn = ToggleButton(text=option, state=state, size_hint_y=None, height=50)
            self.buttons.append(btn)
        self.value = [btn.text for btn in self.buttons if btn.state == 'down']
        App.get_running_app().set_fav_sfx(self)
        self.buttons.clear()

    def _create_options(self):
        main_scr = App.get_running_app().get_main_screen()
        toolbar = main_scr.get_toolbar()
        self.options = toolbar.sfx_list
        App.get_running_app().set_fav_sfx(self)


