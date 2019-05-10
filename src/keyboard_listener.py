from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.app import App
from character_select import CharacterSelect
from character import Character, characters
from location import location_manager
import os


class KeyboardListener(Widget):

    def __init__(self, **kwargs):
        super(KeyboardListener, self).__init__(**kwargs)
        self.keyboard_shortcuts = None
        self.load_shortcuts()

    def load_shortcuts(self):
        config = App.get_running_app().config
        self.keyboard_shortcuts = {
            config.get('keybindings', 'open_character_select'): self.open_character_select,
            config.get('keybindings', 'open_inventory'): self.open_inventory,
            config.get('keybindings', 'refresh'): self.refresh
        }

    def bind_keyboard(self):
        Window.bind(on_key_down=self._on_keyboard_down)

    def _on_keyboard_down(self, inst, value, keycode, text, modifiers):
        if text is None:
            return
        shortcut = ""
        if modifiers:
            for mod in modifiers:
                shortcut += str(mod)
                shortcut += "+"
        shortcut += text
        if shortcut in self.keyboard_shortcuts:
            shortcut_hook = self.keyboard_shortcuts[shortcut]
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

    def open_inventory(self):
        main_scr = App.get_running_app().get_main_screen()
        user = App.get_running_app().get_user()
        user.inventory.open()
        toolbar = main_scr.get_toolbar()
        toolbar.text_item_btn.text = "no item"

    def refresh(self):
        from mainscreen import RightClickMenu
        user = App.get_running_app().get_user()
        location_manager.is_loaded = False
        location_manager.get_locations()
        RightClickMenu.on_loc_select(None, None, user.location.name)
        self.refresh_characters()
        main_scr = App.get_running_app().get_main_screen()
        toolbar = main_scr.get_toolbar()
        toolbar.sfx_dropdown.clear_widgets()
        toolbar.sfx_list = []
        toolbar.load_sfx()
        toolbar.create_sfx_dropdown()
        main_scr.left_tab.music_list.ready()
        user.get_char().nsfw_sprites = {}
        user.get_char().spoiler_sprites = {}
        user.get_char().cg_sprites = {}
        try:
            user.get_char().read_config()
        except AttributeError:
            pass
        user.set_char(user.get_char())
        user.get_char().load()
        main_scr.on_new_char(user.get_char())

    @staticmethod
    def refresh_characters():
        characters.clear()
        char = {name: Character(name) for name in os.listdir("characters") if os.path.isdir("characters/" + name)}
        characters.update(char)
