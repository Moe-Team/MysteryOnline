from kivy.config import Config, ConfigParser
from kivy.utils import platform
import os

Config.set('kivy', 'log_name', 'MO_%y-%m-%d_%_.txt')
Config.set('kivy', 'log_dir', os.getcwd()+'/kivy_logs')
Config.set('kivy', 'desktop', 1)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('kivy', 'exit_on_escape', 0)
if platform == "win":
    Config.set('kivy', 'window_icon', 'icon.ico')
else:
    Config.set('kivy', 'window_icon', 'icon.png')
config = ConfigParser()
try:
    config.read('mysteryonline.ini')
    Config.set('graphics', 'width', int(config.get('display', 'resolution').split('x', 1)[0]))
    Config.set('graphics', 'height', int(config.get('display', 'resolution').split('x', 1)[1]))
except:
    Config.set('graphics', 'width', 1366)
    Config.set('graphics', 'height', 768)
    pass
