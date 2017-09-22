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
        self.counter = 0

    def ready(self):
        self.grid_l.bind(minimum_height=self.grid_l.setter('height'))
        self.grid_l.add_widget(self.log)

    def add_special_entry(self, msg):
        self.log.text += msg

    def add_entry(self, msg, username):
        if self.counter == 100:
            self.counter = 0
            self.log = LogLabel()
            self.grid_l.add_widget(self.log)
            self.log.bind(on_ref_press=self.copy_text)
        self.log.text += "{0}: [ref={2}]{1}[/ref]\n".format(username, msg, self.remove_markup(msg))
        self.counter += 1
        config = App.get_running_app().config
        if config.getdefaultint('other', 'log_scrolling', 1):
            self.scroll_y = 0
        now = datetime.now()
        cur_date = now.strftime("%d-%m-%Y")
        cur_time = now.strftime("%H:%M:%S")
        msg = self.remove_markup(msg)
        log_msg = "<{} {}> {}: {}\n".format(cur_time, cur_date, username, msg)
        with open('msg_log.txt', 'a', encoding='utf-8') as f:
            f.write(log_msg)

    def copy_text(self, inst, value):
        if 'www.' in value or 'http://' in value or 'https://' in value:
            pattern = re.compile(r'(https?://)?[-a-zA-Z0-9@:%._+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_+.~#?&/=]*)')
            url = re.search(pattern, value)
            if url:
                webbrowser.open(url.group(0))
            return
        value = value.replace('&bl;', '[').replace('&br;', ']').replace('&amp', '&')
        Clipboard.copy(value)

    def remove_markup(self, msg):
        pattern = re.compile(r'\[/?color.*?\]')
        msg = re.sub(pattern, '', msg)
        return msg