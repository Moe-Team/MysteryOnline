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
        self.last_pos = 0
        self.counter = 0
        self.distance_to_top = 0
        self.original_size = []

    def ready(self):
        self.grid_l.bind(minimum_height=self.grid_l.setter('height'))
        self.grid_l.add_widget(self.log)
        self.original_size = self.viewport_size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_mouse_scrolling:
                self.last_pos = (self.vbar[0] * self.viewport_size[1]) + self.original_size[1]
                print("mouse registered", self.original_size[1], self.last_pos, self.viewport_size, self.vbar[0])
        return super(LogWindow, self).on_touch_down(touch)

    def add_entry(self, msg, *args):
        self.log.text += msg
        config = App.get_running_app().config
        if config.getdefaultint('other', 'log_scrolling', 1):
            self.scroll_y = 0
        else:
            bar_position = self.last_pos - self.original_size[1]
            if not bar_position:  # if the bar is at the bottom
                self.scroll_y = 0
            else:  # when the scrollbar is at the top, it will go up by 300pixels and then go back to the first message.
                self.distance_to_top = self.viewport_size[1] - self.last_pos
                distance_to_scroll_x, distance_to_scroll_y = self.convert_distance_to_scroll(0, self.distance_to_top)
                self.scroll_y = distance_to_scroll_y
                '''After 8 hours of trying to solve an issue, the problem was because I initialized original_size
                to viewport_size in the init and didn't know why it gave me 0 back instead of its actual height.
                Programming is all tears and suffering.
                Had a breakdown writing it. Here's what I made. Probably not quite I wanted it to do, but it looks 
                good.'''

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
