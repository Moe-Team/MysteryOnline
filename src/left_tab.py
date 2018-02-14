from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.uix.recycleview import RecycleView
from utils import binary_search
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView


class SectionLabel(Label):

    def __init__(self, **kwargs):
        super(SectionLabel, self).__init__(**kwargs)


class SubSectionLabel(Label):

    def __init__(self, **kwargs):
        super(SubSectionLabel, self).__init__(**kwargs)


class TrackSection:

    def __init__(self, name):
        self.name = name
        self.subsections = {}
        self.tracks = []

    def add_subsection(self, subsection):
        self.subsections[subsection.get_name()] = subsection

    def add_track(self, track_name):
        self.tracks.append(track_name)

    def get_name(self):
        return self.name

    def get_subsections(self):
        return self.subsections

    def get_tracks(self):
        return self.tracks


class TrackSubSection:

    def __init__(self, name):
        self.name = name
        self.tracks = []

    def add_track(self, track_name):
        self.tracks.append(track_name)

    def get_name(self):
        return self.name

    def get_tracks(self):
        return self.tracks


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
            encoded_url = self.text + ";" + self.track_url
            main_scr.ooc_window.music_tab.on_music_play(encoded_url)


class MusicListView(RecycleView):

    def __init__(self, **kwargs):
        super(MusicListView, self).__init__(**kwargs)


class SearchResults(ScrollView):

    def __init__(self, **kwargs):
        super(SearchResults, self).__init__(**kwargs)
        self.scroll_type = ['bars']
        self.bar_width = 10

    def add_label(self, label):
        self.children[0].add_widget(label)

    def clear_labels(self):
        self.children[0].clear_widgets()


class MusicList(TabbedPanelItem):
    music_list_view = ObjectProperty(None)
    search_bar = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MusicList, self).__init__(**kwargs)
        self.temp_data = []
        self.tracks = {}
        self.search_space = []
        self.track_search_space = []
        self.section_search_space = []
        self.subsection_search_space = []
        self.sections = {}
        self.subsections = {}
        self.search_results = SearchResults()
        self.search_done = False
        self.current_section = None
        self.current_subsection = None

    def ready(self):
        self.load_tracks()

    def load_tracks(self):
        try:
            with open('musiclist.txt', mode='r', encoding='utf-16') as f:
                for line in f:
                    if len(line) > 2:
                        self.build_from_line(line)
        except FileNotFoundError:
            Logger.warning('Music: musiclist.txt not found')
            return
        self.music_list_view.data = self.temp_data
        self.track_search_space = list(self.tracks.keys())
        self.section_search_space = list(self.sections.keys())
        self.subsection_search_space = list(self.subsections.keys())
        self.track_search_space.sort(key=str.lower)
        self.section_search_space.sort(key=str.lower)
        self.subsection_search_space.sort(key=str.lower)

    def build_from_line(self, line):
        if line.startswith('['):
            section = line[1:-2]
            prop_dict = {'text': section, 'color': [0.8, 0, 0, 1]}
            track_section = TrackSection(section)
            self.sections[section.lower()] = track_section
            self.current_section = track_section
            self.current_subsection = None
        elif line.startswith('<'):
            subsection = line[1:-2]
            prop_dict = {'text': subsection, 'color': [0, 0.8, 0, 1]}
            track_subsection = TrackSubSection(subsection)
            self.subsections[subsection.lower()] = track_subsection
            self.current_subsection = track_subsection
            self.current_section.add_subsection(track_subsection)
        elif line.startswith('\\'):
            subsubsection = line[1:-2]
            prop_dict = {'text': subsubsection, 'color': [0, 0, 0.8, 1]}
        else:
            track_name, track_url = line.split(':', 1)
            track_url = track_url.strip()
            prop_dict = {'text': track_name, 'track_url': track_url, 'color': [1, 1, 1, 1]}
            self.tracks[track_name.lower()] = [track_name, track_url, self.current_section, self.current_subsection]
            if self.current_subsection is None:
                self.current_section.add_track(track_name)
            else:
                self.current_subsection.add_track(track_name)
        prop_dict['size_hint_x'] = 1
        prop_dict['size_hint_y'] = None
        prop_dict['height'] = 30
        self.temp_data.append(prop_dict)

    def search(self, target):
        if target == "":
            self.clear_search()
            return
        if self.search_done:
            self.clear_search()
        self.search_bar.text = ""
        Clock.schedule_once(self.refocus)
        is_section = False
        is_subsection = False
        if target.startswith('['):
            target = target.strip('[]')
            is_section = True
            self.search_space = self.section_search_space
        elif target.startswith('<'):
            target = target.strip('<>')
            is_subsection = True
            self.search_space = self.subsection_search_space
        else:
            self.search_space = self.track_search_space
        result = self.find_track(target)
        if result is None:
            return
        for track in result:
            if is_section and track in self.sections:
                section = self.sections[track]
                self.add_section_to_search_result(section)
                for section_track in section.get_tracks():
                    self.add_track_to_search_result(section_track)
                for subsection_name, subsection in section.get_subsections().items():
                    self.add_subsection_to_search_result(subsection)
                    for track_name in subsection.get_tracks():
                        self.add_track_to_search_result(track_name)
            elif is_subsection and track in self.subsections:
                subsection = self.subsections[track]
                self.add_subsection_to_search_result(subsection)
                for track_name in subsection.get_tracks():
                    self.add_track_to_search_result(track_name)
            elif not is_subsection and not is_section:
                track_section = self.tracks[track.lower()][2]
                self.add_section_to_search_result(track_section)
                track_subsection = self.tracks[track.lower()][3]
                if track_subsection is not None:
                    self.add_subsection_to_search_result(track_subsection)
                self.add_track_to_search_result(track)
        layout = self.content
        layout.remove_widget(self.music_list_view)
        layout.add_widget(self.search_results, index=1)

    def add_subsection_to_search_result(self, subsection):
        subsection_label = SubSectionLabel()
        subsection_label.text = subsection.get_name()
        self.search_results.add_label(subsection_label)

    def add_section_to_search_result(self, section):
        section_label = SectionLabel()
        section_label.text = section.get_name()
        self.search_results.add_label(section_label)

    def add_track_to_search_result(self, track):
        track_label = TrackLabel(size_hint_x=1, size_hint_y=None, height=30)
        track_label.text = self.tracks[track.lower()][0]
        track_label.track_url = self.tracks[track.lower()][1]
        self.search_results.add_label(track_label)

    def find_track(self, target):
        found_index = binary_search(self.search_space, target)
        if found_index is None:
            return None
        self.search_done = True
        i = found_index
        current_track = self.search_space[i].lower()
        result = []
        while current_track.startswith(target.lower()):
            result.append(current_track)
            if i == len(self.search_space) - 1:
                break
            i += 1
            current_track = self.search_space[i].lower()
        i = found_index
        if i > 0:
            i -= 1
            current_track = self.search_space[i].lower()
            while current_track.startswith(target.lower()):
                result.append(current_track)
                if i == 0:
                    break
                i -= 1
                current_track = self.search_space[i].lower()
        return result

    def refocus(self, *args):
        self.search_bar.focus = True

    def clear_search(self):
        if not self.search_done:
            return
        self.search_done = False
        self.search_results.clear_labels()
        layout = self.content
        layout.remove_widget(self.search_results)
        layout.add_widget(self.music_list_view, index=1)


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
