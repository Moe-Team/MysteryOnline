from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen

from character_select import CharacterSelect
from location import location_manager
from debug_mode import DebugModePopup

from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

class RightClickMenu(ModalView):
    loc_button = ObjectProperty(None)
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

    def on_loc_select_clicked(self, *args):
        self.create_loc_drop()
        loc_drop_main_button = Button(size_hint=(None,None), size = (200, 30))     #Temporary button just for dropdown
        self.get_parent_window().add_widget(loc_drop_main_button)
        loc_drop_main_button.pos = (self.loc_button.x + self.loc_button.width, self.loc_button.y + self.loc_button.height)
        self.loc_drop.open(loc_drop_main_button)           
        self.get_parent_window().remove_widget(loc_drop_main_button)               #And the temporary button is gone, R.I.P.

    def create_location_buttons(self, loc_list):
        for l in location_manager.get_locations():
            btn = Button(text=l, size_hint=(None, None), size=(200, 30))
            btn.bind(on_release=lambda btn_: self.loc_drop.select(btn_.text))
            loc_list.add_widget(btn)
        loc_list.bind(on_select=self.on_loc_select)

    def create_loc_drop(self):
        self.loc_drop = DropDown(size_hint=(None, None), size=(200, 30))
        self.create_location_buttons(self.loc_drop)
        self.loc_drop.bind(on_select=self.on_loc_select_clicked)
        
    def on_loc_select(self, inst, loc_name):
        main_scr = App.get_running_app().get_main_screen()
        user_handler = App.get_running_app().get_user_handler()
        loc = location_manager.get_locations()[loc_name]
        user_handler.set_current_loc(loc)
        main_scr.sprite_settings.update_sub(loc)
        main_scr.sprite_preview.set_subloc(user_handler.get_current_subloc())


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
    music_name_display = ObjectProperty(None)

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
        locations = location_manager.get_locations()
        user_handler.set_current_loc(locations['Hakuryou'])
        self.sprite_settings.update_sub(locations['Hakuryou'])
        self.toolbar.set_user(self.user)
        self.sprite_preview.set_subloc(user_handler.get_current_subloc())
        char = self.user.get_char()
        if char is not None:
            self.on_new_char(char)
        App.get_running_app().keyboard_listener.bind_keyboard()

    def on_new_char(self, char):
        self.msg_input.readonly = False
        self.icons_layout.load_icons(char)
        self.set_first_sprite(char)
        user_handler = App.get_running_app().get_user_handler()
        connection_manager = user_handler.get_connection_manager()
        message_factory = App.get_running_app().get_message_factory()
        message = message_factory.build_character_message(char.name)
        connection_manager.send_msg(message)
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
