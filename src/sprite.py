from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget


class SpriteSettings(BoxLayout):
    check_flip_h = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SpriteSettings, self).__init__(**kwargs)
        self.functions = {"flip_h": self.flip_sprite}
        self.activated = []
        self.flipped = []

    def apply_post_processing(self, sprite, setting):
        if setting == 0:
            if sprite not in self.flipped:
                self.flip_sprite(sprite)
                self.flipped.append(sprite)
        else:
            if sprite in self.flipped:
                self.flip_sprite(sprite)
                self.flipped.remove(sprite)
        return sprite

    def flip_sprite(self, sprite):
        sprite.flip_horizontal()

    def on_checked_flip_h(self, value):
        user_handler = App.get_running_app().get_user_handler()
        if value:
            user_handler.set_current_sprite_option(0)
        else:
            user_handler.set_current_sprite_option(1)
        sprite = user_handler.get_current_sprite()
        sprite_option = user_handler.get_current_sprite_option()
        sprite = self.apply_post_processing(sprite, sprite_option)
        main_scr = App.get_running_app().get_main_screen()
        main_scr.sprite_preview.set_sprite(sprite)
        Clock.schedule_once(main_scr.refocus_text, 0.2)


class SpritePreview(Image):
    center_sprite = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SpritePreview, self).__init__(**kwargs)

    def set_subloc(self, sub):
        self.texture = sub.get_img().texture

    def set_sprite(self, sprite):
        self.center_sprite.texture = None
        self.center_sprite.texture = sprite
        self.center_sprite.opacity = 1
        self.center_sprite.size = (self.center_sprite.texture.width / 3,
                                   self.center_sprite.texture.height / 3)


class SpriteWindow(Widget):
    background = ObjectProperty(None)
    sprite_layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(SpriteWindow, self).__init__(**kwargs)
        self.center_sprite = Image(opacity=0, size_hint=(None, None), size=(600, 600),
                                   pos_hint={'center_x': 0.5, 'y': 0})
        self.left_sprite = Image(opacity=0, size_hint=(None, None), size=(600, 600),
                                 pos_hint={'center_x': 0.25, 'y': 0})
        self.right_sprite = Image(opacity=0, size_hint=(None, None), size=(600, 600),
                                  pos_hint={'center_x': 0.75, 'y': 0})

    def set_sprite(self, user):
        subloc = user.get_subloc()
        pos = user.get_pos()
        self.sprite_layout.clear_widgets()
        if pos == 'right':
            self.sprite_layout.add_widget(self.center_sprite, index=2)
            self.sprite_layout.add_widget(self.right_sprite, index=0)
            self.sprite_layout.add_widget(self.left_sprite, index=1)
            subloc.add_r_user(user)
        elif pos == 'left':
            self.sprite_layout.add_widget(self.center_sprite, index=1)
            self.sprite_layout.add_widget(self.right_sprite, index=2)
            self.sprite_layout.add_widget(self.left_sprite, index=0)
            subloc.add_l_user(user)
        else:
            self.sprite_layout.add_widget(self.center_sprite, index=0)
            self.sprite_layout.add_widget(self.right_sprite, index=2)
            self.sprite_layout.add_widget(self.left_sprite, index=1)
            subloc.add_c_user(user)

        self.display_sub(subloc)

    def set_subloc(self, subloc):
        self.background.texture = subloc.get_img().texture

    def display_sub(self, subloc):
        if subloc.c_users:
            sprite = subloc.get_c_user().get_current_sprite()
            option = subloc.get_c_user().get_sprite_option()
            main_scr = App.get_running_app().get_main_screen()
            sprite = main_scr.sprite_settings.apply_post_processing(sprite, option)
            if sprite is not None:
                self.center_sprite.texture = None
                self.center_sprite.texture = sprite
                self.center_sprite.opacity = 1
                self.center_sprite.size = self.center_sprite.texture.size
        else:
            self.center_sprite.texture = None
            self.center_sprite.opacity = 0
        if subloc.l_users:
            sprite = subloc.get_l_user().get_current_sprite()
            option = subloc.get_l_user().get_sprite_option()
            main_scr = App.get_running_app().get_main_screen()
            sprite = main_scr.sprite_settings.apply_post_processing(sprite, option)
            if sprite is not None:
                self.left_sprite.texture = None
                self.left_sprite.texture = sprite
                self.left_sprite.opacity = 1
                self.left_sprite.size = self.left_sprite.texture.size
        else:
            self.left_sprite.texture = None
            self.left_sprite.opacity = 0
        if subloc.r_users:
            sprite = subloc.get_r_user().get_current_sprite()
            option = subloc.get_r_user().get_sprite_option()
            main_scr = App.get_running_app().get_main_screen()
            sprite = main_scr.sprite_settings.apply_post_processing(sprite, option)
            if sprite is not None:
                self.right_sprite.texture = None
                self.right_sprite.texture = sprite
                self.right_sprite.opacity = 1
                self.right_sprite.size = self.right_sprite.texture.size
        else:
            self.right_sprite.texture = None
            self.right_sprite.opacity = 0
