import re
import random
from MysteryOnline.dicegame import dice_game
from MysteryOnline.mainscreen import RightClickMenu
from MysteryOnline.sprite import SpriteSettings
from kivy.app import App
from kivy.core.window import Window
from MysteryOnline.character import characters
from MysteryOnline.mopopup import MOPopup


class CommandError(Exception):
    pass


class CommandPrefixNotFoundError(CommandError):

    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual


class CommandUnknownArgumentTypeError(CommandError):

    def __init__(self, type_):
        self.type_ = type_


class CommandInvalidArgumentsError(CommandError):
    pass


class CommandNoArgumentsError(CommandError):
    pass


class Command:

    def __init__(self, cmd_name, args=None):
        self.cmd_name = cmd_name
        self.args = args
        self.process_name = 'process_' + self.cmd_name
        self.process = None

    def __getitem__(self, item):
        return self.args[item]

    def __str__(self):
        return str(self.args)

    def __repr__(self):
        return str(self)

    def get_name(self):
        return self.cmd_name

    def get_process(self):
        return self.process

    def execute(self, command_proc):
        self.process = getattr(command_proc, self.process_name)
        self.process()


class CommandHandler:

    def __init__(self, cmd_name, form=None):
        self.cmd_name = cmd_name
        self.types = []
        self.names = []
        if form is not None:
            self.num_of_args = None
            self.parse_format(form)
        else:
            self.num_of_args = 0

    def parse_format(self, form):
        args = form.split(' ')
        self.num_of_args = len(args)
        for arg in args:
            type_, name = arg.split(':')
            self.types.append(type_)
            self.names.append(name)

    def parse_command(self, msg):
        if self.num_of_args == 0:
            return Command(self.cmd_name)
        args = self.split_msg_into_args(msg, self.num_of_args)
        args_processed = {}
        for i, arg in enumerate(args):
            if self.types[i] == 'str':
                arg = str(arg)
            elif self.types[i] == 'int':
                arg = int(arg)
            elif self.types[i] == 'float':
                arg = float(arg)
            else:
                raise CommandUnknownArgumentTypeError(self.types[i])
            args_processed[self.names[i]] = arg
        command = Command(self.cmd_name, args_processed)
        return command

    def split_msg_into_args(self, msg, num_of_args):
        args = []
        mark = None
        start_index = None
        for w in msg.split(' ', num_of_args):
            if w.startswith(("'", '"')):
                mark = w[0]
                args.append(w[1:])
                start_index = len(args) - 1
                continue
            if mark is not None:
                if w.endswith(mark):
                    args[start_index] += " " + w[:-1]
                    mark = None
                    start_index = None
                else:
                    args[start_index] += " " + w
            else:
                args.append(w)
        return args


class RegexCommandHandler:

    def __init__(self, cmd_name, arg_names, pattern):
        self.cmd_name = cmd_name
        self.pattern = re.compile(pattern)
        self.arg_names = arg_names

    def parse_command(self, cmd):
        if cmd is None:
            raise CommandNoArgumentsError
        found = re.search(self.pattern, cmd)
        if found is None:
            raise CommandInvalidArgumentsError
        arg_number = len(self.arg_names)
        args = {}
        for i in range(arg_number):
            group_number = i + 1  # Offset by 1 because group 0 is the whole string
            args[self.arg_names[i]] = found.group(group_number)
        return Command(self.cmd_name, args)


class CommandProcessor:

    def __init__(self):
        self.command = None
        self.shortcuts = {}
        self.handlers = {
            'roll': RegexCommandHandler('roll', ['no_of_dice', 'die_type', 'mod'],
                                        r'(\d*)?\s*(d[\d\w]*)\s*([+-]\s*\d*)?'),
            'clear': CommandHandler('clear'),

            'clean': CommandHandler('clear'),

            'color': RegexCommandHandler('color', ['color', 'text'],
                                         r'([a-z]*)\s*["\'](.*)["\']$'),
            'refresh': CommandHandler('refresh'),

            'choice': RegexCommandHandler('choice', ['list_of_users', 'choice_text', 'options'],
                                          '(@.*\S)? *"(.*)"\s*"(.*)"'),
            'move': CommandHandler('move', 'str:location'),

            'subloc': CommandHandler('subloc', 'str:sublocation'),

            'startim': CommandHandler('startim'),

            'random': CommandHandler('random', 'str:option'),

            'help': CommandHandler('help'),

            'nickname': CommandHandler('nickname', 'str:newNick')
        }

    def process_command(self, cmd_name, cmd):
        if cmd_name in self.handlers:
            cmd_handler = self.handlers[cmd_name]
        else:
            return None
        args = cmd_handler.parse_command(cmd)
        self.command = Command(cmd_name, args)
        self.command.execute(self)

    #                       #
    # v Command Processes v #
    #                       #

    def process_roll(self):
        try:
            dice_game.process_input(self.command)
        except ValueError:
            temp_pop = MOPopup("Command error", "Rolling format is: xdy+z", "OK")
            temp_pop.open()

    def process_clear(self):
        main_scr = App.get_running_app().get_main_screen()
        app = App.get_running_app()
        textbox = main_scr.text_box
        user = App.get_running_app().get_user()
        if textbox.prev_user == user and textbox.is_displaying_msg is False:
            connection_manager = App.get_running_app().get_user_handler().get_connection_manager()
            message_factory = App.get_running_app().get_message_factory()
            location = app.get_user_handler().get_current_loc().name
            message = message_factory.build_clear_message(location)
            connection_manager.send_msg(message)
            connection_manager.send_local(message)

    def process_clean(self):
        self.process_clear()

    def process_color(self):
        user_handler = App.get_running_app().get_user_handler()
        user = user_handler.get_user()
        user.set_color(self.command['color'])
        user_handler.send_message(self.command['text'])
        user.set_color('normal')

    def process_refresh(self):
        App.get_running_app().keyboard_listener.refresh()

    def process_choice(self):
        user_handler = App.get_running_app().get_user_handler()
        username = user_handler.get_user().username
        connection_manager = user_handler.get_connection_manager()
        message_factory = App.get_running_app().get_message_factory()
        message = message_factory.build_choice_message(username, self.command['choice_text'],
                                                       self.command['options'], self.command['list_of_users'])
        connection_manager.send_msg(message)
        connection_manager.send_local(message)

    # noinspection PyTypeChecker
    def process_move(self):
        # TODO Don't use the class instead of its instance pls, gotta find a way around this
        RightClickMenu.on_loc_select(None, None, self.command['location'])

    def process_subloc(self):
        app = App.get_running_app()
        main_scr = App.get_running_app().get_main_screen()
        sprite_settings = main_scr.sprite_settings
        sublocations = app.get_user_handler().get_current_loc().sublocations
        try:
            subloc = sublocations[self.command['sublocation']]
            sprite_settings.on_subloc_select(None, subloc.get_name())
        except KeyError:
            try:
                for subloc in sublocations:
                    if (self.command['sublocation']).lower() in sublocations[subloc].get_name().lower():
                        sprite_settings.on_subloc_select(None, subloc)
            except IndexError:
                pass

    def process_nickname(self):
        new_nickname = self.command['newNick']
        message_factory = App.get_running_app().get_message_factory()
        user_handler = App.get_running_app().get_user_handler()
        connection_manager = user_handler.get_connection_manager()
        message = message_factory.change_nickname_message(new_nickname)
        connection_manager.send_msg(message)
        connection_manager.send_local(message)
        user = App.get_running_app().get_user()
        user.username = new_nickname

    def process_random(self):
        user = App.get_running_app().get_user()
        user_handler = App.get_running_app().get_user_handler()
        main_scr = App.get_running_app().get_main_screen()
        if self.command['option'].lower() == 'char' or self.command['option'].lower() == 'character':
            user.set_char((random.choice(list(characters.values()))))
            user.get_char().load()
            main_scr.on_new_char(user.get_char())
        elif self.command['option'].lower() == 'subloc' or self.command['option'].lower() == 'sublocation':
            user_handler.set_chosen_subloc_name(random.choice(user.get_loc().list_sub()))
            main_scr.sprite_preview.set_subloc(user_handler.get_chosen_subloc())
        elif self.command['option'].lower() == 'music' or self.command['option'].lower() == 'track':
            try:
                main_scr.left_tab.music_list.tracks[
                    random.choice(list(main_scr.left_tab.music_list.tracks))].on_selected()
            except IndexError:
                pass
        else:
            print('no random option found')
            pass

    def process_startim(self):
        Window.set_title("Sonata's Revenge")

    def process_help(self):
        log = App.get_running_app().get_main_screen().log_window
        log.add_entry("\nAvailable commands:\n")
        for i in self.handlers:
            log.add_entry("/{0}\n".format(i))
        log.add_entry("\n")
    #                       #
    # ^ Command Processes ^ #
    #                       #

    def load_shortcuts(self):
        config = App.get_running_app().config
        for shortcut in config.items('command-shortcuts'):
            self.shortcuts[shortcut[0]] = shortcut[1]

    def get_commands(self):
        return list(self.handlers)


command_processor = CommandProcessor()
