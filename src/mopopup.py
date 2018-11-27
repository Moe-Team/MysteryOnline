from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView


class MOPopupBase(Popup):
    def __init__(self, title_, msg, *args, **kwargs):
        super(MOPopupBase, self).__init__(**kwargs)
        self.box_lay = None
        self.create_box_layout(msg)
        self.size_popup()
        self.title = title_

    def needs_button(self, dismissable, btn_command):
        if dismissable:
            return True
        if btn_command is None:
            return False
        for command in btn_command:
            if command is not None:
                return True
        return False

    def create_box_layout(self, msg):
        self.box_lay = BoxLayout(orientation='vertical')
        self.content = self.box_lay
        self.content.add_widget(Label(text=msg))

    def add_buttons(self, btn_msg, dismissable, btn_command=None, btn_command_args=None):
        btn_command = [] if btn_command is None else btn_command
        btn_command_args = [] if btn_command_args is None else btn_command_args
        number_of_buttons = len(btn_msg)
        for btn in range(number_of_buttons):
            try:
                command = btn_command[btn]
            except IndexError:
                command = None
            if command is None:
                args = None
            else:
                args = btn_command_args[btn]
            self.create_button(btn_msg[btn], dismissable, command, args)        

    def create_button(self, btn_msg, dismissable, btn_command, btn_command_args=None):
        btn_command_args = [] if btn_command_args is None else btn_command_args
        btn = Button(text=btn_msg, size_hint=(1, 0.4))
        self.content.add_widget(btn)
        btn_command = self.create_command(dismissable, btn_command, btn_command_args)
        btn.bind(on_press=btn_command)        

    def create_command(self, dismissable, btn_command, args):
        if btn_command is None:
            return self.dismiss
        if dismissable:
            dismiss = self.dismiss

            def execute_and_dismiss(self):
                btn_command(*args)
                dismiss()
            return execute_and_dismiss
        else:
            def execute(self):
                btn_command(*args)
            return execute

    def size_popup(self, size_hint=(None, None), size=(400, 200)):
        self.size_hint = size_hint
        self.size = size
    

class MOPopup(MOPopupBase):

    def __init__(self, title_, msg, btn_msg, dismissable=True, btn_command=None,
                 btn_command_args=None, *args, **kwargs):
        btn_command_args = [] if btn_command_args is None else btn_command_args
        super().__init__(title_, msg, **kwargs)
        if self.needs_button(dismissable, btn_command):
            self.create_button(btn_msg, dismissable, btn_command, btn_command_args)
        else:
            self.auto_dismiss = False
        

class MOPopupYN(MOPopupBase):
    def __init__(self, title_, msg, btn_command=[None, None], btn_command_args=[[None], [None]], btn_msg=['Yes', 'No'],
                 dismissable=True):
        super().__init__(title_, msg)
        if self.needs_button(dismissable, btn_command):
            self.add_buttons(btn_msg, dismissable, btn_command, btn_command_args)
        else:
            self.auto_dismiss = False


class MOPopupFile(Popup):
    def __init__(self, title, file, *args, **kwargs):
        super(MOPopupFile, self).__init__(**kwargs)
        self.title = title
        self.size_hint = (None, None)
        self.size = [400, 600]
        scroll = ScrollView(size_hint=[1, 1], size=[self.width, self.height - 50])
        try:
            file = open(file)
        except FileNotFoundError:
            popup = MOPopup("Error", "file not found", "Whatever you say, mate")
            popup.open()
            return
        label = Label(text=file.read(), markup=True, size_hint_y=None,
                      size=[scroll.width, 600], text_size=[scroll.width, None],
                      halign='center', valign='top', padding_x=60)
        label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        scroll.add_widget(label)
        box_lay = BoxLayout(orientation='vertical')
        box_lay.add_widget(scroll)
        content = box_lay
        self.add_widget(content)
