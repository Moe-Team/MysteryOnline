import user
from mopopup import MOPopupBase
from kivy.uix.checkbox import CheckBox
from kivy.app import App

class ChoicePopup(MOPopupBase):

    def __init__(self, title_, sender, msg, btn_msg, user, **kwargs):
        super().__init__(title_, msg, **kwargs)
        self.user_handler = App.get_running_app().get_user_handler()
        self.number_of_buttons = len(btn_msg)
        self.sender = sender
        self.btn_msg = btn_msg
        self.add_buttons(btn_msg, True, self.build_btn_commands_list(), self.build_btn_args_list())
        self.add_checkbox()
        self.whisper = False
        self.selected_option = None

    def on_dismiss(self):
        self.send_answer()

    def option_select(self, option):
        self.selected_option = option

    def send_answer(self):
        connection_manager = App.get_running_app().get_user_handler().get_connection_manager()
        message_factory = App.get_running_app().get_message_factory()
        username = self.user_handler.get_user().username
        message = message_factory.build_choice_return_message(username, self.sender, self.whisper, self.selected_option)
        connection_manager.send_msg(message)
        connection_manager.send_local(message)
           
    def build_btn_commands_list(self):
        btn_commands_list = []
        for i in range(self.number_of_buttons):
            btn_commands_list.append(self.option_select)
        return btn_commands_list

    def build_btn_args_list(self):
        btn_args_list = []
        for msg in self.btn_msg:
            msg = msg.replace('\;',';')
            btn_args_list.append([msg])
        return btn_args_list

    def add_checkbox(self):
        checkbox = CheckBox()
        checkbox.bind(active=self.on_checkbox_active)
        self.content.add_widget(checkbox)

    def on_checkbox_active(self, checkbox, value):
        self.set_whisper(value)

    def set_whisper(self, value):
        self.whisper = value
            
        
            
            
