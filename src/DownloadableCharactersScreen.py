import os
import requests
from zipfile import ZipFile
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.app import App


class DownloadableCharactersScreen(Popup):
    main_window = ObjectProperty(None)
    scroll_lay = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(DownloadableCharactersScreen, self).__init__(**kwargs)
        self.missing_characters_seen = []
        self.fill_popup()

    def fill_popup(self):
        user = App.get_running_app().get_user()
        main_scr = App.get_running_app().get_main_screen()
        ooc = main_scr.ooc_window
        self.download_rar("Shizuka")

    def download_rar(self, char):
        shared_link = 'https://drive.google.com/open?id=1Uo2Hivdv_-mS1qNUDZKwKnj5SMRY0Mck'
        file_id = shared_link.split('id=')
        direct_link = 'https://drive.google.com/uc?export=download&id=' + file_id[1]
        path = 'characters/'+char+'.zip'
        r = requests.get(direct_link, allow_redirects=True)
        open(path, 'wb').write(r.content)
        with ZipFile(path) as zipArch:
            zipArch.extractall("characters")
        os.remove(path)
