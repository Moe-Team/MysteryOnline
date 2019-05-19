import re
import webbrowser
from datetime import datetime

from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView


class LogLabel(Label):
    def __init__(self, **kwargs):
        super(LogLabel, self).__init__(**kwargs)


class LogWindow(ScrollView):
    grid_l = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LogWindow, self).__init__(**kwargs)
        self.log = LogLabel()
        self.log.bind(on_ref_press=self.copy_text)
        self.scrollable_distance = 0
        self.counter = 0
        self.distance_to_top = 0
        self.original_size = []
        self.last_viewport_size = 0

    def ready(self):
        self.grid_l.bind(minimum_height=self.grid_l.setter('height'), size=self.maintain_scrolling)
        self.grid_l.add_widget(self.log)
        self.original_size = self.viewport_size

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_mouse_scrolling or touch.button == 'left':
                self.distance_to_top = (1 - self.scroll_y) * self.scrollable_distance
        return super(LogWindow, self).on_touch_up(touch)

    def on_scroll_stop(self, touch, check_children=True):
        if self.collide_point(*touch.pos):
            if touch.button == 'left':
                self.distance_to_top = (1 - self.scroll_y) * self.scrollable_distance
        return super(LogWindow, self).on_scroll_stop(touch)

    def maintain_scrolling(self, *args):
        self.scrollable_distance = self.original_size[1] - self.viewport_size[1]
        if self.scroll_y > 0:
            self.scroll_y = 1 - self.distance_to_top / self.scrollable_distance

    '''thank you https://gist.github.com/tshirtman/41e533d077567762b3bd981f718f3cd6 for the auto scroll fix'''

    def add_entry(self, msg, *args):
        self.log.text += msg
        config = App.get_running_app().config
        if config.getdefaultint('other', 'log_scrolling', 1):
            self.scroll_y = 0

    def add_chat_entry(self, msg, username):
        if self.counter == 100:
            self.add_new_label()
        self.add_entry("{0}: [ref={2}]{1}[/ref]\n".format(username, msg, self.remove_markup(msg)))
        self.counter += 1
        self.write_text_log(msg, username)

    def write_text_log(self, msg, username):
        now = datetime.now()
        cur_date = now.strftime("%d-%m-%Y")
        cur_time = now.strftime("%H:%M:%S")
        msg = self.remove_markup(msg)
        log_msg = "<{} {}> {}: {}\n".format(cur_time, cur_date, username, msg)
        with open('msg_log.txt', 'a', encoding='utf-8') as f:
            f.write(log_msg)

    def add_new_label(self):
        self.counter = 0
        self.log = LogLabel()
        self.grid_l.add_widget(self.log)
        self.log.bind(on_ref_press=self.copy_text)

    def copy_text(self, inst, text):
        if self.contains_link(text):
            self.open_url(text)
        else:
            text = text.replace('&bl;', '[').replace('&br;', ']').replace('&amp', '&')
            Clipboard.copy(text)

    def contains_link(self, message):
        return 'www.' in message or 'http://' in message or 'https://' in message

    def open_url(self, value):
        pattern = re.compile(r'(https?://)?[-a-zA-Z0-9@:%._+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_+.~#?&/=!]*)')
        url = re.search(pattern, value)
        if url:
            webbrowser.open(url.group(0))

    def remove_markup(self, msg):
        pattern = re.compile(r'\[/?color.*?\]')
        msg = re.sub(pattern, '', msg)
        return msg
