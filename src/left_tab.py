from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.uix.recycleview import RecycleView


class TrackLabel(Label):

    def __init__(self, **kwargs):
        super(TrackLabel, self).__init__(**kwargs)
        self.track_url = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == 'left' and touch.is_double_tap:
                self.on_selected()

    def on_selected(self):
        if self.track_url:
            main_scr = App.get_running_app().get_main_screen()
            main_scr.ooc_window.music_tab.on_music_play(self.track_url)


class MusicListView(RecycleView):

    def __init__(self, **kwargs):
        super(MusicListView, self).__init__(**kwargs)


class MusicList(TabbedPanelItem):
    music_list_view = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MusicList, self).__init__(**kwargs)
        self.temp_data = []

    def ready(self):
        self.load_tracks()

    def load_tracks(self):
        try:
            with open('musiclist.txt', mode='r') as f:
                for line in f:
                    self.build_from_line(line)
        except FileNotFoundError:
            Logger.warning('Music: musiclist.txt not found')
            return
        self.music_list_view.data = self.temp_data

    def build_from_line(self, line):
        if line.startswith('['):
            section = line[1:-2]
            prop_dict = {'text': section, 'color': [0.8, 0, 0, 1]}
        elif line.startswith('<'):
            subsection = line[1:-2]
            prop_dict = {'text': subsection, 'color': [0, 0.8, 0, 1]}
        elif line.startswith('\\'):
            subsubsection = line[1:-2]
            prop_dict = {'text': subsubsection, 'color': [0, 0, 0.8, 1]}
        else:
            track_name, track_url = line.split(':', 1)
            track_url = track_url.strip()
            prop_dict = {'text': track_name, 'track_url': track_url, 'color': [1, 1, 1, 1]}
        prop_dict['size_hint_x'] = 1
        prop_dict['size_hint_y'] = None
        prop_dict['height'] = 30
        self.temp_data.append(prop_dict)


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
