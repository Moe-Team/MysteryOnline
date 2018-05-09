from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class MOPopupBase(Popup):
    def __init__(self, title_, msg, *args, **kwargs):
        super(MOPopupBase, self).__init__(**kwargs)
        self.create_box_layout(msg)
        self.size_popup()
        self.title = title_
        self.box_lay = None

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

    def add_buttons(self, btn_msg, dismissable, btn_command=[], btn_command_args=[]):
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

    def create_button(self, btn_msg, dismissable, btn_command, btn_command_args=[]):
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

    def __init__(self, title_, msg, btn_msg, dismissable=True, btn_command=None, btn_command_args=[], *args, **kwargs):
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
