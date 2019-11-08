from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.modalview import ModalView
import gc


class Icon(Image):
    def __init__(self, name, texture, **kwargs):
        super(Icon, self).__init__(**kwargs)
        self.name = name
        self.texture = texture
        self.size_hint = None, None
        self.size = 40, 40

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.parent.sprite_picked(self, self.name)
            return True

    def display_tooltip(self, *args):
        if not self.parent or not self.parent.parent:
            return
        if len(Window.children) > 1:
            return
        self.parent.parent.on_hover_in(self.name)

    def close_tooltip(self, *args):
        if not self.parent or not self.parent.parent:
            return
        self.parent.parent.on_hover_out()


class IconModal(ModalView):

    def __init__(self, **kwargs):
        super(IconModal, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        pass


class IconsLayout(BoxLayout):
    current_page = NumericProperty(1)

    def __init__(self, **kwargs):
        super(IconsLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.grids = []
        self.current_icon = None
        self.hover_popup = IconModal(size_hint=(None, None), background_color=[0, 0, 0, 0],
                                     background='misc_img/transparent.png')
        self.scheduled_icon = None
        self.max_pages = 0
        self.loading = False
        Window.bind(mouse_pos=self.on_mouse_pos)

    def prev_page(self, *args):
        if self.current_page > 1:
            self.current_page -= 1

    def next_page(self, *args):
        if self.current_page < self.max_pages:
            self.current_page += 1

    def on_current_page(self, *args):
        if not self.loading:
            self.remove_widget(self.children[1])
            grid_index = self.current_page - 1
            self.add_widget(self.grids[grid_index], index=1)

    def on_mouse_pos(self, window, pos):
        if len(self.grids) == 0 or App.get_running_app().config.getdefaultint('other', 'sprite_tooltips', 1) == 0:
            return

        if not self.collide_point(*pos):
            if self.scheduled_icon is not None:
                Clock.unschedule(self.scheduled_icon.display_tooltip)
                self.scheduled_icon.close_tooltip()
            return

        for child in self.grids[self.current_page-1].children:
            if not isinstance(child, Icon):
                continue

            if child.collide_point(*pos):
                Clock.schedule_once(child.display_tooltip, 0.4)
                self.scheduled_icon = child
                break
            else:
                Clock.unschedule(child.display_tooltip)  # cancel scheduled event since I moved the cursor
                child.close_tooltip()  # close if it's opened

    def load_icons(self, char):
        icons = char.get_icons()
        spoiler_icons = char.get_spoiler_icons()
        config = App.get_running_app().config
        if len(self.children) > 1:
            self.remove_widget(self.children[1])
        for g in self.grids:
            g.clear_widgets()
        del self.grids[:]
        counter = 0
        g = None
        for i in sorted(icons.textures.keys()):
            if counter % 54 == 0:
                g = GridLayout(cols=6)
                self.grids.append(g)
            if config.getdefaultint('other', 'spoiler_mode', 1) and i in spoiler_icons:
                from character import characters
                red_herring = characters['RedHerring']
                red_herring.load()
                spoiler_icon = red_herring.get_icons()['4']
                g.add_widget(Icon(i, spoiler_icon))
            else:
                g.add_widget(Icon(i, icons[i]))
            counter += 1
        self.max_pages = len(self.grids)
        self.loading = True
        self.current_page = 1
        self.add_widget(self.grids[0], index=1)
        self.sprite_picked(self.grids[0].children[-1], None, True)
        self.sprite_picked(self.grids[0].children[-1], None, False)
        self.loading = False

    def sprite_picked(self, icon, sprite_name=None, current=False):
        if sprite_name is None:
            sprite_name = icon.name
        main_scr = App.get_running_app().get_main_screen()
        user_handler = App.get_running_app().get_user_handler()
        if current:
            user_handler.set_current_sprite_name(sprite_name)
            sprite = user_handler.get_current_sprite()
            setting = user_handler.get_current_sprite_option
        else:
            user_handler.set_chosen_sprite_name(sprite_name)
            sprite = user_handler.get_chosen_sprite()
            setting = user_handler.get_chosen_sprite_option
        sprite = main_scr.sprite_settings.apply_post_processing(sprite, setting)
        main_scr.sprite_preview.set_sprite(sprite)
        Clock.schedule_once(main_scr.refocus_text, 0.2)
        if self.current_icon is not None:
            self.current_icon.color = [1, 1, 1, 1]
        icon.color = [0.3, 0.3, 0.3, 1]
        self.current_icon = icon

    def on_hover_in(self, sprite_name):
        if self.hover_popup.get_parent_window():
            return
        gc.collect()
        main_scr = App.get_running_app().get_main_screen()
        char = main_scr.user.get_char()
        user_handler = App.get_running_app().get_user_handler()
        sprite_option = user_handler.get_chosen_sprite_option()
        sprite = char.get_sprite(sprite_name)
        main_scr.sprite_settings.apply_post_processing(sprite, sprite_option)
        sprite_texture = char.get_sprite(sprite_name).get_texture()
        sprite_size = sprite_texture.size
        # Can't use absolute position so it uses a workaround
        hover_x = self.right / Window.width
        hover_y = self.y / Window.height
        sprite_size = sprite_size[0] * 0.8, sprite_size[1] * 0.8
        im = Image()
        im.texture = sprite_texture
        im.size = sprite_texture.size
        self.hover_popup.add_widget(im)
        self.hover_popup.size = sprite_size
        self.hover_popup.pos_hint = {'x': hover_x, 'y': hover_y}
        self.hover_popup.open()

    def on_hover_out(self):
        if self.hover_popup.get_parent_window():
            self.hover_popup.clear_widgets()
            self.hover_popup.dismiss(animation=False)

    def on_scroll_start(self, *args):
        super(IconsLayout, self).on_scroll_start(*args)
        if self.scheduled_icon:
            Clock.unschedule(self.scheduled_icon.display_tooltip)
