import user
from mopopup import MOPopup_Base
from kivy.app import App

class ChoicePopup(MOPopup_Base):

    def __init__(self, title_, sender, msg, btn_msg, user, **kwargs):
        super().__init__(title_, msg, **kwargs)
        self.user_handler = App.get_running_app().get_user_handler()
        self.number_of_buttons = len(btn_msg)
        self.sender = sender
        self.btn_msg = btn_msg
        self.add_buttons(btn_msg, True, self.build_btn_commands_list(), self.build_btn_args_list())
        self.whisper = True
        self.refused_to_answer = True

    def on_dismiss(self):
        if self.refused_to_answer:
            print('refused to answer')
            #log.add_entry(self.user_handler.get_user().username + ' refused to answer.')
            


    def option_select(self, option):
        connection_manager = App.get_running_app().get_user_handler().get_connection_manager()
        message_factory = App.get_running_app().get_message_factory()
        username = self.user_handler.get_user().username
        self.refused_to_answer = False
        message = message_factory.build_choice_return_message(username, self.sender, self.whisper, option)
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
            
            
