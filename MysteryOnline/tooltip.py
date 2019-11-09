from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget


class TooltipBehavior(Widget):
    def __init__(self, **kwargs):
        super(TooltipBehavior, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)
        self.popup = None

    def on_mouse_pos(self, *args):
        if not self.parent or not self.parent.parent:
            return
        if not self.get_root_window():
            return
        pos = args[1]
        Clock.unschedule(self.display_tooltip)  # cancel scheduled event since I moved the cursor
        self.close_tooltip()  # close if it's opened
        if self.collide_point(*self.to_widget(*pos)):
            Clock.schedule_once(self.display_tooltip, 0.4)

    def display_tooltip(self, *args):
        if not self.parent or not self.parent.parent:
            return
        if len(Window.children) > 1:
            return
        self.set_new_popup()
        self.reposition()
        self.popup.open()

    def close_tooltip(self, *args):
        if not self.parent or not self.parent.parent:
            return
        self.popup.dismiss()

    def reposition(self):
        x, y = self.to_window(self.x, self.y)
        menu_x = x / Window.width
        menu_y = y / Window.height
        if y >= self.popup.height:
            loc_y = 'top'
        else:
            loc_y = 'y'
        self.popup.pos_hint = {'x': menu_x, loc_y: menu_y}

    def set_new_popup(self):
        pass
