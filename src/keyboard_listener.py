from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.app import App
from character_select import CharacterSelect


class KeyboardListener(Widget):

    def __init__(self, **kwargs):
        super(KeyboardListener, self).__init__(**kwargs)
        self.keyboard_shortcuts = None
        self.load_shortcuts()

    def load_shortcuts(self):
        self.keyboard_shortcuts = {
            ('ctrl', 'p'): self.open_character_select
        }

    def bind_keyboard(self):
        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, inst, value, keycode, text, modifiers):
        if not modifiers:
            return
        if (modifiers[0], text) in self.keyboard_shortcuts:
            shortcut_hook = self.keyboard_shortcuts[(modifiers[0], text)]
            shortcut_hook()
            return True

    def open_character_select(self):
        cs = CharacterSelect()
        cs.bind(on_dismiss=self.on_picked)
        cs.open()

    def on_picked(self, inst):
        user = App.get_running_app().get_user()
        if inst.picked_char is not None:
            user.set_char(inst.picked_char)
            user.get_char().load()
            main_scr = App.get_running_app().get_main_screen()
            main_scr.on_new_char(user.get_char())
