from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen

from character_select import CharacterSelect
from location import locations
from debug_mode import DebugModePopup


class RightClickMenu(ModalView):
    char_select = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(RightClickMenu, self).__init__(**kwargs)
        self.background_color = [0, 0, 0, 0]

    def on_char_select_clicked(self, *args):
        cs = CharacterSelect()
        self.dismiss(animation=False)
        cs.bind(on_dismiss=self.on_picked)
        cs.open()

    def on_settings_clicked(self, *args):
        App.get_running_app().open_settings()
        self.dismiss(animation=False)

    def on_inventory_clicked(self, *args):
        main_scr = App.get_running_app().get_main_screen()
        user = App.get_running_app().get_user()
        user.inventory.open()
        toolbar = main_scr.get_toolbar()
        toolbar.text_item_btn.text = "no item"
        self.dismiss(animation=False)

    def on_debug_menu_clicked(self, *args):
        popup = DebugModePopup()
        self.dismiss(animation=False)
        popup.open()

    def on_picked(self, inst):
        user = App.get_running_app().get_user()
        if inst.picked_char is not None:
            user.set_char(inst.picked_char)
            user.get_char().load()
            main_scr = App.get_running_app().get_main_screen()
            main_scr.on_new_char(user.get_char())


class MainScreen(Screen):
    icons_layout = ObjectProperty(None)
    sprite_preview = ObjectProperty(None)
    sprite_window = ObjectProperty(None)
    msg_input = ObjectProperty(None)
    toolbar = ObjectProperty(None)
    text_box = ObjectProperty(None)
    log_window = ObjectProperty(None)
    ooc_window = ObjectProperty(None)
    left_tab = ObjectProperty(None)
    sprite_settings = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.user = None
        self.users = {}
        App.get_running_app().set_main_screen(self)
        self.config = App.get_running_app().config

    def on_stop(self):
        pass

    def on_touch_down(self, touch):
        if touch.button == 'right':
            self.on_right_click(touch)
            return True
        super(MainScreen, self).on_touch_down(touch)

    def on_right_click(self, touch):
        menu = RightClickMenu()
        # Can't use absolute position so it uses a workaround
        loc_y, menu_x, menu_y = self.calculate_popup_position(menu, touch)
        menu.pos_hint = {'x': menu_x, loc_y: menu_y}
        menu.open()

    def calculate_popup_position(self, menu, touch):
        menu_x = touch.pos[0] / Window.width
        menu_y = touch.pos[1] / Window.height
        if touch.pos[1] >= menu.height:
            loc_y = 'top'
        else:
            loc_y = 'y'
        return loc_y, menu_x, menu_y

    def on_ready(self, *args):
        """Called when mainscreen becomes active"""

        self.msg_input.ready(self)
        self.left_tab.ready(self)
        self.ooc_window.ready(self)
        self.log_window.ready()
        user_handler = App.get_running_app().get_user_handler()
        user_handler.set_current_loc(locations['Hakuryou'])
        self.toolbar.update_loc()
        self.toolbar.update_sub(locations['Hakuryou'])
        self.toolbar.set_user(self.user)
        self.sprite_preview.set_subloc(user_handler.get_current_subloc())
        char = self.user.get_char()
        if char is not None:
            self.on_new_char(char)

    def on_new_char(self, char):
        self.msg_input.readonly = False
        self.icons_layout.load_icons(char)
        self.set_first_sprite(char)
        user_handler = App.get_running_app().get_user_handler()
        connection_manager = user_handler.get_connection_manager()
        connection_manager.send_char_to_all(char.name)
        connection_manager.update_char(self, char.name, self.user.username)

    def set_first_sprite(self, char):
        first_icon = sorted(char.get_icons().textures.keys())[0]
        first_sprite = char.get_sprite(first_icon)
        self.sprite_preview.set_sprite(first_sprite)

    def refocus_text(self, *args):
        # Refocusing the text input has to be done this way cause Kivy
        self.msg_input.focus = True

    def get_toolbar(self):
        return self.toolbar
