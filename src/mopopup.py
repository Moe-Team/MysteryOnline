from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


class MOPopup(Popup):

    def __init__(self, title_, msg, btn_msg, dismissable=True, btn_command=None, btn_command_args=[], *args, **kwargs):
        self.box_lay = BoxLayout(orientation='vertical')
        self.content = self.box_lay
        self.content.add_widget(Label(text=msg))
        if dismissable or btn_command is not None:
            btn = Button(text=btn_msg, size_hint=(1, 0.4))
            self.content.add_widget(btn)
            if dismissable:
                btn_command = self.add_dismiss_to_command(btn_command, *btn_command_args)               
            btn.bind(on_press=btn_command)
        else:
            self.auto_dismiss = False
        self.title = title_
        self.size_hint = (None, None)
        self.size = (400, 200)
        super(MOPopup, self).__init__(**kwargs)

    def add_dismiss_to_command(self, btn_command, *args):
        if btn_command is None:
            return self.dismiss
        dismiss = self.dismiss
        def execute_and_dismiss(self):
            btn_command(*args)
            dismiss()
        return execute_and_dismiss

        
