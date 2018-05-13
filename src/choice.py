import user
from mopopup import MOPopupBase
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.app import App

class ChoicePopup(MOPopupBase):

    def __init__(self, title_, sender, msg, btn_msg, user, **kwargs):
        self.number_of_buttons = len(btn_msg)
        self.grid_lay = None
        super().__init__(title_, msg, **kwargs)
        self.user_handler = App.get_running_app().get_user_handler()
        self.sender = sender
        self.btn_msg = btn_msg
        self.add_buttons(btn_msg, True, self.build_btn_commands_list(), self.build_btn_args_list())
        self.whisper = False
        self.selected_option = None
        self.size_popup(size=(400,400))

    def create_box_layout(self, msg):
        super().create_box_layout(msg)
        if self.number_of_buttons > 8:
            number_of_cols = int(self.number_of_buttons/8)+1
            self.grid_lay = GridLayout(cols=number_of_cols)
            self.content = self.grid_lay
            

    def open(self, *args, **kwargs):
        if self.grid_lay is not None:
            self.content = self.box_lay
            self.content.add_widget(self.grid_lay)
        self.add_checkbox()
        super().open(*args, **kwargs)

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
        checkbox_grid = GridLayout(cols=2, row_force_default=True, row_default_height=40)
        checkbox = CheckBox(size_hint_x=None, width=50)
        checkbox_grid.add_widget(checkbox)
        checkbox.bind(active=self.on_checkbox_active)
        checkbox_grid.add_widget(Label(text='Whisper', size_hint_x=None, width=50))
        self.box_lay.add_widget(checkbox_grid)

    def on_checkbox_active(self, checkbox, value):
        self.set_whisper(value)

    def set_whisper(self, value):
        self.whisper = value
            
        
            
            
