from kivy.uix.popup import Popup


class CharacterSelect(Popup):

    def __init__(self, **kwargs):
        super(CharacterSelect, self).__init__(**kwargs)
        self.title = "Select your character"
        self.size_hint = (0.7, 0.7)
