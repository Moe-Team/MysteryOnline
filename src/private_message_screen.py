from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.utils import escape_markup
from kivy.uix.image import Image
from kivy.uix.label import Label

from irc_mo import PrivateConversation
from character import characters


class PrivateMessageScreen(ModalView):
    pm_body = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PrivateMessageScreen, self).__init__(**kwargs)
        self.conversations = []
        self.irc = None
        self.username = ''
        self.avatar = None
        self.current_conversation = None
        self.conversation_list = getattr(self.ids, 'prv_users_list')
        self.text_box = getattr(self.ids, 'pm_input')
        self.pm_close_sound = SoundLoader.load('sounds/general/codecover.wav')
        self.pm_window_open_flag = False
        self.pm_flag = False
        self.pm_body.bind(minimum_height=self.pm_body.setter('height'))

    def ready(self):
        user = App.get_running_app().get_user()
        self.avatar = user.get_char().avatar

    def set_current_conversation(self, conversation):
        self.current_conversation = conversation

    def open_conversation(self, conversation):
        self.set_current_conversation(conversation)
        self.pm_body.clear_widgets()
        self.update_pms()

    def get_conversation_for_user(self, username):
        if len(self.conversations) is 0:
            self.build_conversation(username)
            return self.get_conversation_for_user(username)
        else:
            for c in self.conversations:
                if c.username == username:
                    return c

    def set_current_conversation_user(self, username):
        conversation = self.get_conversation_for_user(username)
        self.current_conversation = conversation

    def prv_chat_close_btn(self):
        vol = App.get_running_app().config.getdefaultint('sound', 'effect_volume', 100)
        self.pm_close_sound.volume = vol / 100
        self.pm_close_sound.play()
        self.pm_window_open_flag = False
        self.pm_flag = False
        self.dismiss()

    def build_conversation(self, username):
        is_init = False
        if username is not self.username:
            for c in self.conversations:
                if username == c.username:
                    is_init = True
            if not is_init:
                self.add_conversation(username)

    def add_conversation(self, username):
        conversation = PrivateConversation()
        conversation.username = username
        self.conversations.append(conversation)
        btn = Button(text=username, size_hint_y=None, height=50, width=self.conversation_list.width)
        btn.bind(on_press=lambda x: self.open_conversation(conversation))
        self.conversation_list.add_widget(btn)
        self.current_conversation = conversation

    def update_conversation(self, sender, msg):
        if 'www.' in msg or 'http://' in msg or 'https://' in msg:
            msg = "[u]{}[/u]".format(msg)
        self.current_conversation.msgs += "{0}: [ref={2}]{1}[/ref]\n".format(sender, msg, escape_markup(msg))
        self.pm_body.clear_widgets()
        self.update_pms()

    def update_pms(self):
        user = App.get_running_app().get_user()
        main_scr = App.get_running_app().get_main_screen()
        ooc = main_scr.ooc_window
        for line in self.current_conversation.msgs.splitlines():
            username = line.split(':', 1)[0]
            if username == self.current_conversation.username:
                try:
                    avatar = Image(source=characters[ooc.online_users
                                   [self.current_conversation.username].char_lbl_text].avatar, size_hint_x=None, width=60)  # Placeholder until we do better
                except ValueError:
                    avatar = Image(source=characters['RedHerring'].avatar, size_hint_x=None, width=60)
            else:
                avatar = Image(source=user.get_char().avatar, size_hint_x=None, width=60)
            self.pm_body.add_widget(avatar)
            self.pm_body.add_widget(Label(text=line, markup=True, on_ref_press=main_scr.log_window.copy_text))
        self.pm_body.parent.scroll_y = 0

    def refocus_text(self, *args):
        self.text_box.focus = True

    def send_pm(self):
        sender = self.username
        main_scr = App.get_running_app().get_main_screen()
        user = App.get_running_app().get_user()
        self.avatar = Image(source=user.get_char().avatar, size_hint_x=None, width=60)
        if self.current_conversation is not None:
            if self.text_box.text != "":
                    receiver = self.current_conversation.username
                    self.irc.send_private_msg(receiver, sender, self.text_box.text)
                    msg = self.text_box.text
                    if 'www.' in msg or 'http://' in msg or 'https://' in msg:
                        msg = "[u]{}[/u]".format(msg)
                    self.pm_body.add_widget(self.avatar)
                    self.current_conversation.msgs += "{0}: [ref={2}]{1}[/ref]\n".format(sender, msg,
                                                                                                escape_markup(msg))
                    self.pm_body.add_widget(Label(text="{0}: [ref={2}]{1}[/ref]\n".format(sender, msg,
                                                                                          escape_markup(msg)), markup=True,
                                                  on_ref_press=main_scr.log_window.copy_text))
                    self.text_box.text = ''
                    self.pm_body.parent.scroll_y = 0
                    Clock.schedule_once(self.refocus_text, 0.1)
