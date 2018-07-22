import user
from mopopup import MOPopupBase
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.app import App

class ChoicePopup(MOPopupBase):

    def __init__(self, title_, sender, msg, btn_msg, user, **kwargs):
        self.number_of_buttons = len(btn_msg)
        super().__init__(title_, msg, **kwargs)
        self.size_popup(size=(400,400))
        self.user_handler = App.get_running_app().get_user_handler()
        self.user = self.user_handler.get_user()
        self.grid_lay = None
        self.questioner = sender
        self.options = self.clean_options(btn_msg)
        self.selected_option = None
        self.whisper = False
        self.username = self.user.username
        self.add_buttons(self.options, True, self.build_btn_commands_list(), self.build_btn_args_list())

    def create_box_layout(self, msg):
        super().create_box_layout(msg)
        if self.number_of_buttons > 8:
            number_of_cols = int(self.number_of_buttons/8)+1
            self.grid_lay = GridLayout(cols=number_of_cols)
            self.content = self.grid_lay
            
    def open(self, *args, **kwargs):
        if self.is_user_busy():
            return
        if self.grid_lay is not None:
            self.content = self.box_lay
            self.content.add_widget(self.grid_lay)
        self.add_checkbox()
        self.user.set_choice_popup_state(True)
        super().open(*args, **kwargs)

    def on_dismiss(self):
        self.user.set_choice_popup_state(False)
        if self.selected_option is None:
            self.whisper = 'Refused'
        self.send_answer()

    def option_select(self, option):
        self.selected_option = option

    def send_answer(self):
        connection_manager = App.get_running_app().get_user_handler().get_connection_manager()
        message_factory = App.get_running_app().get_message_factory()
        message = message_factory.build_choice_return_message(self.username, self.questioner, self.whisper, self.selected_option)
        connection_manager.send_msg(message)
        connection_manager.send_local(message)
           
    def build_btn_commands_list(self):
        btn_commands_list = []
        for i in range(self.number_of_buttons):
            btn_commands_list.append(self.option_select)
        return btn_commands_list

    def build_btn_args_list(self):
        btn_args_list = []
        for msg in self.options:
            btn_args_list.append([msg])
        return btn_args_list

    def clean_options(self, options):
        cleaned_options = []
        for option in options:
            option = option.replace('\;', ';')
            cleaned_options.append(option)
        return cleaned_options

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

    def is_user_busy(self):
        if self.user.has_choice_popup:
            self.set_whisper('Busy')
            self.send_answer()
            return True
        return False

    def get_questioner(self):
        return self.questioner

    def get_options(self):
        return self.options

    def get_selected_option(self):
        return self.selected_option
        
            
        
            
            
