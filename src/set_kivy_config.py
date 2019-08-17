from kivy.config import Config, ConfigParser
import os

Config.set('kivy', 'log_name', 'MO_%y-%m-%d_%_.txt')
Config.set('kivy', 'log_dir', os.getcwd()+'/kivy_logs')
Config.set('kivy', 'desktop', 1)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('kivy', 'exit_on_escape', 0)
Config.set('kivy', 'window_icon', 'icon.ico')
config = ConfigParser()
try:
    config.read('mysteryonline.ini')
    Config.set('graphics', 'width', int(config.get('display', 'resolution').split('x', 1)[0]))
    Config.set('graphics', 'height', int(config.get('display', 'resolution').split('x', 1)[1]))
except:
    pass
