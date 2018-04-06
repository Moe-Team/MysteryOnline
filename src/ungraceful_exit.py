from kivy.app import App
from mopopup import MOPopup
import configparser

def was_last_exit_graceful(config):
    config = App.get_running_app().config
    graceful_exit = config.getboolean('other', 'graceful_exit')
    if graceful_exit:
        return True
    return False

def show_ungraceful_exit_popup(config):
    popup = MOPopup('Ungraceful Exit','It seems MO closed unexpectedly last time.\n'
                    'Do you wish to send us the error log?','No')
    popup.open()

def set_graceful_flag(config, boolean):
    config = App.get_running_app().config
    config.set('other', 'graceful_exit', str(boolean))

