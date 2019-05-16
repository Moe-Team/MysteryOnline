from kivy.config import Config, ConfigParser

Config.set('kivy', 'desktop', 1)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('kivy', 'exit_on_escape', 0)
Config.set('kivy', 'window_icon', 'icon.ico')
config = ConfigParser()
config.read('mysteryonline.ini')
Config.set('graphics', 'width', int(config.get('display', 'resolution').split('x', 1)[0]))
Config.set('graphics', 'height', int(config.get('display', 'resolution').split('x', 1)[1]))
