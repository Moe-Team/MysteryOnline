import configparser
import os
import requests
from zipfile import ZipFile
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.app import App
from keyboard_listener import KeyboardListener
from kivy.uix.button import Button
from kivy.config import ConfigParser


class DownloadableCharactersScreen(Popup):
    main_window = ObjectProperty(None)
    scroll_lay = ObjectProperty(None)
    download_all_button = ObjectProperty(None)
    dlc_window = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(DownloadableCharactersScreen, self).__init__(**kwargs)
        self.fill_popup()

    def fill_popup(self):
        self.download_all_button.bind(on_press=lambda x: self.download_all())
        dlc_list = App.get_running_app().get_main_screen().character_list_for_dlc
        for text in dlc_list:
            arguments = text.split('#', 1)
            char = arguments[0]
            link = arguments[1]
            button = Button(text=char, size_hint_y=None, height=50, width=self.width)
            button.bind(on_press=lambda x: self.download_character(char, link))
            self.dlc_window.add_widget(button)

    def download_character(self, char_name, link):
        file_id = link.split('id=')
        direct_link = 'https://drive.google.com/uc?export=download&id=' + file_id[1]
        path = 'characters/' + char_name + '.zip'
        r = requests.get(direct_link, allow_redirects=True)
        open(path, 'wb').write(r.content)
        with ZipFile(path) as zipArch:
            zipArch.extractall("characters")
        os.remove(path)
        dlc_list = App.get_running_app().get_main_screen().character_list_for_dlc
        char = char_name + '#' + link
        dlc_list.remove(char)
        self.overwrite_ini(char_name, link)
        KeyboardListener.refresh_characters()
        self.dismiss(animation=False)

    def download_all(self):
        dlc_list = App.get_running_app().get_main_screen().character_list_for_dlc
        for text in dlc_list:
            arguments = text.split('#', 1)
            char = arguments[0]
            shared_link = arguments[1]
            file_id = shared_link.split('id=')
            direct_link = 'https://drive.google.com/uc?export=download&id=' + file_id[1]
            path = 'characters/'+char+'.zip'
            r = requests.get(direct_link, allow_redirects=True)
            open(path, 'wb').write(r.content)
            with ZipFile(path) as zipArch:
                zipArch.extractall("characters")
            os.remove(path)
            char = arguments[0] + '#' + arguments[1]
            dlc_list.remove(char)
            self.overwrite_ini(arguments[0], arguments[1])
            KeyboardListener.refresh_characters()
            self.dismiss(animation=False)

    def overwrite_ini(self, char_name, link):
        config = configparser.ConfigParser()
        path = "characters/{0}/".format(char_name)
        config.read(path + "settings.ini")
        char = config['character']
        char['download'] = link
        with open(path + "settings.ini", 'w') as configfile:
            config.write(configfile)
