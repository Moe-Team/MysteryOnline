from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label


class TrackLabel(Label):

    def __init__(self, track_name, track_url, **kwargs):
        super(TrackLabel, self).__init__(**kwargs)
        self.text = track_name
        self.track_url = track_url

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == 'left' and touch.is_double_tap:
                self.on_selected()

    def on_selected(self):
        main_scr = App.get_running_app().get_main_screen()
        main_scr.ooc_window.music_tab.on_music_play(self.track_url)


class MusicList(TabbedPanelItem):
    music_lay = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MusicList, self).__init__(**kwargs)

    def ready(self):
        self.music_lay.bind(minimum_height=self.music_lay.setter('height'))
        self.load_tracks()

    def load_tracks(self):
        try:
            with open('musiclist.txt', mode='r') as f:
                for line in f:
                    track_name, track_url = line.split(':', 1)
                    self.music_lay.add_widget(TrackLabel(track_name, track_url))
        except FileNotFoundError:
            print("No music list found")


class LeftTab(TabbedPanel):
    sprite_preview = ObjectProperty(None)
    sprite_settings = ObjectProperty(None)
    trans_slider = ObjectProperty(None)
    speed_slider = ObjectProperty(None)
    music_list = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LeftTab, self).__init__(**kwargs)

    def ready(self, main_scr):
        main_scr.sprite_preview = self.sprite_preview
        main_scr.sprite_settings = self.sprite_settings
        config = App.get_running_app().config
        self.trans_slider.value = config.getdefaultint('other', 'textbox_transparency', 60)
        self.speed_slider.value = config.getdefaultint('other', 'textbox_speed', 60)
        self.music_list.ready()

    def on_trans_slider_value(self, *args):
        config = App.get_running_app().config
        value = int(self.trans_slider.value)
        config.set('other', 'textbox_transparency', value)

    def on_speed_slider_value(self, *args):
        config = App.get_running_app().config
        value = int(self.speed_slider.value)
        config.set('other', 'textbox_speed', value)
