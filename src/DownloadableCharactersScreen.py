import configparser
import os
import shutil
import requests
from zipfile import ZipFile
import zipfile
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.textinput import TextInput
from keyboard_listener import KeyboardListener
from kivy.uix.button import Button
from mopopup import MOPopup
import threading


class DownloadableCharactersScreen(Popup):
    main_window = ObjectProperty(None)
    scroll_lay = ObjectProperty(None)
    download_all_button = ObjectProperty(None)
    dlc_window = ObjectProperty(None)
    download_from_catalogue_button = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(DownloadableCharactersScreen, self).__init__(**kwargs)
        self.fill_popup()

    def fill_popup(self):
        self.download_all_button.bind(on_press=lambda x: threading.Thread(target=self.download_all, args=()).start())
        dlc_list = App.get_running_app().get_main_screen().character_list_for_dlc
        for text in dlc_list:
            arguments = text.split('#', 2)
            char = arguments[0]
            link = arguments[1]
            ver = arguments[2]
            button = Button(text=char+" {version "+ver+"}", size_hint_y=None, height=50, width=self.width)
            button.bind(on_press=lambda x: threading.Thread(target=self.download_character, args=(char, link, ver)).start())
            self.dlc_window.add_widget(button)

    def get_confirm_token(self, response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def download_character(self, char_name, link, ver):
        try:
            if link.find("drive.google.com") == -1: #checks for google drive link
                try:
                    direct_link = link
                except Exception as e:
                    print("Error: " + e)
            else:
                try:
                    file_id = link.split('id=')
                    try:
                        id = file_id[1]
                        URL = "https://docs.google.com/uc?export=download"

                        session = requests.Session()

                        response = session.get(URL, params={'id': id}, stream=True)
                        token = self.get_confirm_token(response)

                        if token:
                            params = {'id': id, 'confirm': token}
                            response = session.get(URL, params=params, stream=True)

                        direct_link = response.url
                    except IndexError:
                        dlc_list = App.get_running_app().get_main_screen().character_list_for_dlc
                        char = char_name + '#' + link
                        dlc_list.remove(char)
                        self.dismiss()
                        temp_pop = MOPopup("Error downloading", "Can't download " + char_name, "OK")
                        temp_pop.open()
                        return
                except Exception as e:
                    print("Error: " + e)
            try:
                shutil.rmtree('characters/'+char_name)
            except Exception as e:
                print(e)
            path = 'characters/' + char_name + '.zip'
            r = requests.get(direct_link, allow_redirects=True)
            open(path, 'wb').write(r.content)
            with ZipFile(path) as zipArch:
                zipArch.extractall("characters")
            os.remove(path)
            dlc_list = App.get_running_app().get_main_screen().character_list_for_dlc
            char = char_name + '#' + link + '#' + ver
            dlc_list.remove(char)
            self.overwrite_ini(char_name, link, ver)
            KeyboardListener.refresh_characters()
            self.dismiss(animation=False)
            self.clean(char_name)
        except (KeyError, zipfile.BadZipFile) as e:
            print(e)
            self.dismiss()
            temp_pop = MOPopup("Error downloading", "Can't download " + char_name, "OK")
            temp_pop.open()
            return
        except Exception as e:
            print("Error 2: " + e)
        temp_pop = MOPopup("Download complete", "Downloaded " + char_name, "OK")
        temp_pop.open()

    def download_all(self):
        dlc_list = App.get_running_app().get_main_screen().character_list_for_dlc
        for text in dlc_list:
            arguments = text.split('#', 2)
            char = arguments[0]
            shared_link = arguments[1]
            try:
                if shared_link.find("drive.google.com") == -1:  # checks for google drive shared_link
                    try:
                        direct_link = shared_link
                    except Exception as e:
                        print("Error: " + e)
                else:
                    try:
                        file_id = shared_link.split('id=')
                        try:
                            id = file_id[1]
                            URL = "https://docs.google.com/uc?export=download"

                            session = requests.Session()

                            response = session.get(URL, params={'id': id}, stream=True)
                            token = self.get_confirm_token(response)

                            if token:
                                params = {'id': id, 'confirm': token}
                                response = session.get(URL, params=params, stream=True)

                            direct_link = response.url
                        except IndexError:
                            dlc_list = App.get_running_app().get_main_screen().character_list_for_dlc
                            char_link = char + '#' + shared_link
                            dlc_list.remove(char)
                            self.dismiss()
                            temp_pop = MOPopup("Error downloading", "Can't download " + char, "OK")
                            temp_pop.open()
                            return
                    except Exception as e:
                        print("Error: " + e)
                try:
                    shutil.rmtree('characters/' + char)
                except Exception as e:
                    print(e)
                path = 'characters/' + char + '.zip'
                r = requests.get(direct_link, allow_redirects=True)
                open(path, 'wb').write(r.content)
                with ZipFile(path) as zipArch:
                    zipArch.extractall("characters")
                os.remove(path)
                self.clean(arguments[0])
                char = arguments[0] + '#' + arguments[1] + '#' + arguments[2]
                self.overwrite_ini(arguments[0], arguments[1], arguments[2])
            except (KeyError, zipfile.BadZipFile) as e:
                try:
                    dlc_list = App.get_running_app().get_main_screen().character_list_for_dlc
                    char_link = char + '#' + shared_link
                    dlc_list.remove(char_link)
                except ValueError:
                    pass
                temp_pop = MOPopup("Error downloading", "Can't download " + char, "OK")
                temp_pop.open()
            except PermissionError:
                os.remove(path)
                shutil.rmtree('characters/' + char)
                temp_pop = MOPopup("Error downloading", "Can't download " + char + ". Permission Error, character folder deleted, try again.", "OK")
                temp_pop.open()
        App.get_running_app().get_main_screen().character_list_for_dlc = []
        KeyboardListener.refresh_characters()
        temp_pop = MOPopup("Download complete", "You downloaded everything.", "OK")
        temp_pop.open()
        self.dismiss(animation=False)

    def clean(self, char_name):
        path = "characters/{0}/".format(char_name)
        for fname in os.listdir(path):
            fname = fname.lower()
            if not fname.endswith(".png") and not fname.endswith(".atlas") and not fname.endswith(".ini"):
                os.remove(path + fname)

    def overwrite_ini(self, char_name, link, ver):
        config = configparser.ConfigParser()
        path = "characters/{0}/".format(char_name)
        config.read(path + "settings.ini")
        char = config['character']
        char['download'] = link
        char['ver'] = ver
        with open(path + "settings.ini", 'w') as configfile:
            config.write(configfile)

    def download_from_catalogue(self):
        return
