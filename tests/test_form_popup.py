from kivy.app import App
from kivy.uix.button import Button
from MysteryOnline.mopopup import FormPopup
from os import listdir
from kivy.lang.builder import Builder


KV_DIR = "../src/kv_files/"

for kv_file in listdir(KV_DIR):
    Builder.load_file(KV_DIR + kv_file)


class TestApp(App):
    def build(self):
        button = Button(text='Open Popup')
        button.bind(on_release=self.test_popup)
        return button

    def test_popup(self, instance):
        form_popup = FormPopup("test", self.validate_popup, self.submit_popup, self.error_popup)
        form_popup.add_field("Name", is_required=True)
        form_popup.add_field("Description")
        form_popup.open()

    def validate_popup(self, fields):
        print("Validating")
        for field in fields.values():
            if field.text == "error":
                return False
        return True

    def submit_popup(self, popup, fields):
        print("Submitting")
        print(fields)
        popup.dismiss()

    def error_popup(self, popup, fields):
        print("Error")


if __name__ == "__main__":
    TestApp().run()
