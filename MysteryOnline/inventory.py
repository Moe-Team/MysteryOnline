from kivy import Logger
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.core.audio import SoundLoader
from MysteryOnline.mopopup import MOPopup
import webbrowser
import requests
import urllib
import os
import shutil


class UserInventory(Popup):
    main_lay = ObjectProperty(None)
    scroll = ObjectProperty(None)
    item_list = ObjectProperty(None)

    def __init__(self, user,  **kwargs):
        super(UserInventory, self).__init__(**kwargs)
        self.user = user
        self.item_dictionary_logic = {}
        self.number_of_items = len(self.item_dictionary_logic)

    def get_item_string_list(self):
        string_list = []
        for item in self.item_dictionary_logic:
            string_list.append(item)
        return string_list

    def add_item(self, name, description, image_link, user):
        if self.get_item_by_name(name) is None:
            item = Item(name, description, image_link, self, user)
            self.item_dictionary_logic[name] = item
            self.item_list.add_widget(item)
            self.number_of_items += 1
            self.item_list.height = self.number_of_items * 60

    def receive_item(self, name, description, image_link, user):
        item = self.get_item_by_name(name)
        if item is not None:
            self.delete_item(name)
        item = Item(name, description, image_link, self, user)
        self.item_dictionary_logic[name] = item
        self.item_list.add_widget(item)
        config = App.get_running_app().config
        v = config.getdefaultint('sound', 'effect_volume', 100)
        item.open_popup()
        inv_open_sound = SoundLoader.load('sounds/general/takethat.mp3')
        App.get_running_app().play_sound(inv_open_sound, volume=v / 100.0)


    def delete_item(self, name):
        if name in self.item_dictionary_logic:
            self.item_list.remove_widget(self.item_dictionary_logic[name])
            del self.item_dictionary_logic[name]
            self.number_of_items -= 1
            self.item_list.height = self.number_of_items * 60

    def display_item_creator(self):
        item_creator = ItemCreator(self, self.user)
        item_creator.open()

    def get_item_by_name(self, name):
        if name in self.item_dictionary_logic:
            return self.item_dictionary_logic[name]
        else:
            return None

    def send_item(self, item):
        con = App.get_running_app().get_user_handler().get_connection_manager()
        encoded_item = item.encode()
        message_factory = App.get_running_app().get_message_factory()
        message = message_factory.build_item_message(encoded_item)
        con.send_msg(message)
        con.send_local(message)


class Item(GridLayout):
    def __init__(self, name, description, image_link, inventory: UserInventory, username, **kwargs):
        super(Item, self).__init__(**kwargs)
        try:
            os.makedirs('imgcache')
        except FileExistsError:
            Logger.warning("Image Cache Exists.")
        self.size_hint_y = None
        self.height = 50
        self.cols = 3
        self.inventory = inventory
        self.name = Label(text=name)
        self.name.bind(on_touch_down=self.on_item_pressed)
        self.add_widget(self.name)
        self.description = Label(text=description)
        self.image_link = image_link
        try:
            r = requests.get(image_link, timeout=(5, 20))
        except requests.exceptions.MissingSchema:
            return
        r.raise_for_status()
        if r.ok:
            picname = os.path.basename(urllib.parse.urlparse(image_link).path)
            if picname is None:
                picname = "temp.jpg"
            f = open("imgcache/" + picname, mode="wb")
            f.write(r.content)
            f.close()
        self.image = AsyncImage(source="imgcache/"+picname, pos_hint={'left': 1})
        self.image.bind(on_touch_down=self.open_image)
        self.owner_username = username
        delete_btn = Button(text="X", size_hint=[None, 1], width=60)
        delete_btn.bind(on_press=lambda x: self.delete_item())
        self.add_widget(delete_btn)
        self.popup = None
        self.description.text_size = [self.description.size[0]*3, self.description.size[1]]

    def clear_cache(self, instance):
        try:
            shutil.rmtree('imgcache/')
            os.makedirs('imgcache')  #this is the exact same code used for the music cache
        except FileNotFoundError:  #i disgust myself too.
            os.makedirs('imgcache')
        except PermissionError:
            Logger.warning("Cannot clear inventory cache due to permission error.")
        except Exception as e:
            Logger.warning(e)

    def on_item_pressed(self, inst, touch):
        if self.name.collide_point(*touch.pos):
            self.open_popup()

    def get_name(self):
        return self.name.text

    def get_description(self):
        return self.description.text

    def get_image_link(self):
        return self.image

    def get_popup(self):
        return self.popup

    def set_name(self, name):
        self.name = name

    def set_description(self, description):
        self.description = description

    def set_image_link(self, image_link):
        self.image = image_link

    def open_image(self, inst, touch):
        if self.image.collide_point(*touch.pos):
            webbrowser.open(self.image_link)

    def delete_item(self):
        if self.inventory is not None:
            self.inventory.delete_item(self.name.text)

    def build_item_window(self):
        if self.popup is None:
            main_grid = GridLayout(cols=2)
            main_grid.add_widget(self.image)
            main_grid.add_widget(self.description)
            self.popup = Popup(title=self.name.text + " created by " + self.owner_username, content=main_grid,
                               size_hint=(.5, .3), pos_hint={'left': .1,
                                                             'top': 1}, background_color=[0, 0, 0, 0])
        return self.popup

    def open_popup(self):
        popup = self.build_item_window()
        popup.bind(on_dismiss=self.clear_cache)
        popup.open()

    # Encoded by: name#description#image_link#owner_name
    def encode(self):
        return self.name.text+'#'+self.description.text+'#'+self.image_link+'#'+self.owner_username


class ItemCreator(Popup):
    name = ObjectProperty(None)
    description = ObjectProperty(None)
    image_link = ObjectProperty(None)

    def __init__(self, inventory: UserInventory, user, **kwargs):
        super(ItemCreator, self).__init__(**kwargs)
        self.inventory = inventory
        self.user = user
        self.name.pos_hint = {'center_x': 0.5}
        self.description.pos_hint = {'center_x': 0.5}

    def create_item(self, name, description, image_link, user):
        message_len = len(name) + len(description) + len(image_link) + len(user)
        if message_len > 420:
            error_popup = MOPopup("Character limit exceeded", "IRC has a character limit of roughly 500, please make"
                                                              " sure your item's combined description, name, and image"
                                                              " link don't exceed it.", "Close")
            error_popup.size = (900, 200)
            error_popup.open()
            return
        self.inventory.add_item(name, description, image_link, user)
