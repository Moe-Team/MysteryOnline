from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.app import App


class UserInventory(Popup):

    def __init__(self, user,  **kwargs):
        super(UserInventory, self).__init__(**kwargs)
        self.user = user
        self.title = "Inventory"
        self.size_hint = (1, 1)
        self.main_lay = BoxLayout(orientation='vertical', size_hint=(1, None), height=self.height)
        self.scroll = ScrollView(size_hint=(1, None), size=(self.width, self.height - 50))
        self.item_list = GridLayout(cols=1, spacing=10, size_hint_y=0.9, id="item_list")
        self.construct_widget(self)
        self.item_dictionary_logic = {}

    def construct_widget(self, pos):
        close_btn = Button(text="Close", size_hint=(1, 0.1), height=40, pos_hint={'y': 0, 'x': 0})
        close_btn.bind(on_release=self.dismiss)
        add_item_btn = Button(text="+", size_hint=(1, 0.1), height=40, pos_hint={'y': 0, 'x': 0})
        add_item_btn.bind(on_release=lambda x: self.display_item_creator())
        self.scroll.add_widget(self.item_list)
        self.main_lay.add_widget(self.scroll)
        self.main_lay.add_widget(add_item_btn)
        self.main_lay.add_widget(close_btn)
        self.add_widget(self.main_lay)

    def get_item_string_list(self):
        string_list = []
        for item in self.item_dictionary_logic:
            string_list.append(item)
        return string_list

    def add_item(self, name, description, image_link, user):
        item = Item(name, description, image_link, self, user)
        self.item_dictionary_logic[name] = item
        self.item_list.add_widget(item)

    def delete_item(self, name):
        if name in self.item_dictionary_logic:
            self.item_list.remove_widget(self.item_dictionary_logic[name])
            del self.item_dictionary_logic[name]

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
        item_on_str = item.encode()
        con.send_item_to_all(item_on_str)


class Item(GridLayout):
    def __init__(self, name, description, image_link, inventory: UserInventory, username, **kwargs):
        super(Item, self).__init__(**kwargs)
        self.inventory = inventory
        self.cols = 3
        self.name = Label(text=name)
        self.add_widget(self.name)
        self.description = Label(text=description)
        self.image = AsyncImage(source=image_link, pos_hint={'left': 1})
        self.owner_username = username
        delete_btn = Button(text="X")
        delete_btn.bind(on_press=lambda x: self.delete_item())
        self.add_widget(delete_btn)
        self.popup = None

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

    def delete_item(self):
        if self.inventory is not None:
            self.inventory.delete_item(self.name.text)

    def build_item_window(self):
        if self.popup is None:
            main_grid = GridLayout(cols=2)
            main_grid.add_widget(self.image)
            main_grid.add_widget(self.description)
            self.popup = Popup(title=self.name.text + " created by " + self.owner_username, content=main_grid,
                               size_hint=(.6, .2), pos_hint={'left': .1,
                                                             'top': 1})
        return self.popup

    # Encoded by: name#description#image_link#owner_name
    def encode(self):
        return self.name.text+'#'+self.description.text+'#'+self.image.source+'#'+self.owner_username


class ItemCreator(Popup):

    def __init__(self, inventory: UserInventory, user, **kwargs):
        super(ItemCreator, self).__init__(**kwargs)
        self.inventory = inventory
        self.user = user
        self.name = TextInput(text='', multiline=False)
        self.description = TextInput(text='')
        self.image_link = TextInput(text='', multiline=False)
        self.construct_widget(self)

    def construct_widget(self, pos):
        button_grid = GridLayout(cols=2, spacing=10, size_hint_y=0.9)
        text_input_grid = GridLayout(rows=3, spacing=10)
        main_grid = GridLayout(rows=2, spacing=30)
        close_btn = Button(text="Close", size_hint=(1, 0.1), height=40, pos_hint={'y': 0, 'x': 0})
        close_btn.bind(on_release=self.dismiss)
        create_btn = Button(text="Create", size_hint=(1, 0.1), height=40, pos_hint={'y': 0, 'x': 0})
        create_btn.bind(on_release=lambda x: self.create_item(self.name.text, self.description.text,
                                                              self.image_link.text, self.user.username))
        create_btn.bind(on_release=self.dismiss)
        button_grid.add_widget(create_btn)
        button_grid.add_widget(close_btn)
        text_input_grid.add_widget(Label(text="Name: "))
        text_input_grid.add_widget(self.name)
        text_input_grid.add_widget(Label(text="Description: "))
        text_input_grid.add_widget(self.description)
        text_input_grid.add_widget(Label(text="Link: "))
        text_input_grid.add_widget(self.image_link)
        self.add_widget(main_grid)
        main_grid.add_widget(button_grid)
        main_grid.add_widget(text_input_grid)

    def create_item(self, name, description, image_link, user):
        self.inventory.add_item(name, description, image_link, user)
