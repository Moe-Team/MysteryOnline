from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from  kivy.uix.label import Label


class UserInventory(Popup):

    def __init__(self,  **kwargs):
        super(UserInventory, self).__init__(**kwargs)
        self.title = "Inventory"
        self.size_hint = (1, 1)
        self.main_lay = BoxLayout(orientation='vertical', size_hint=(1, None), height=self.height)
        self.scroll = ScrollView(size_hint=(1, None), size=(self.width, self.height - 50))
        self.item_list = GridLayout(cols=1, spacing=10, size_hint_y=0.9, id="item_list")
        self.construct_widget(self)
        self.item_dictionary_logic = {}
        self.add_item("item1", "no", "no")
        #self.add_item("item2", "no", "no")
        #self.remove_widget(self.item_dictionary_logic["item1"])
        #self.delete_item("item1")

    def construct_widget(self, pos):
        close_btn = Button(text="Close", size_hint=(1, 0.1), height=40, pos_hint={'y': 0, 'x': 0})
        close_btn.bind(on_release=self.dismiss)
        self.scroll.add_widget(self.item_list)
        self.main_lay.add_widget(self.scroll)
        self.main_lay.add_widget(close_btn)
        self.add_widget(self.main_lay)

    def get_item_list(self):
        return self.item_dictionary_logic

    def add_item(self, name, description, image_link):
        item = Item(name, description, image_link, self)
        self.item_dictionary_logic[name] = item
        self.item_list.add_widget(item)

    def delete_item(self, name):
        if name in self.item_dictionary_logic:
            self.item_list.remove_widget(self.item_dictionary_logic[name])
            del self.item_dictionary_logic[name]


class Item(GridLayout):
    def __init__(self, name, description, image_link, inventory: UserInventory, **kwargs):
        super(Item, self).__init__(**kwargs)
        self.inventory = inventory
        self.cols = 3
        self.name = Label(text=name)
        self.add_widget(self.name)
        self.description = Label(text=description)
        self.image_link = image_link
        delete_btn = Button(text="X")
        delete_btn.bind(on_press=lambda x: self.delete_item())
        self.add_widget(delete_btn)

    def get_name(self):
        return self.name.text

    def get_description(self):
        return self.description.text

    def get_image_link(self):
        return self.image_link

    def set_name(self, name):
        self.name = name

    def set_description(self, description):
        self.description = description

    def set_image_link(self, image_link):
        self.image_link = image_link

    def delete_item(self):
        if self.inventory is not None:
            self.inventory.delete_item(self.name.text)



