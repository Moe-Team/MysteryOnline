import re
from dicegame import dice_game
from kivy.app import App

import character


class CommandError(Exception):
    pass


class CommandPrefixNotFoundError(CommandError):

    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual


class CommandUnknownArgumentTypeError(CommandError):

    def __init__(self, type_):
        self.type_ = type_


class Command:

    def __init__(self, cmd_name, args=None):
        self.cmd_name = cmd_name
        self.args = args

    def __getitem__(self, item):
        return self.args[item]

    def __str__(self):
        return str(self.args)

    def __repr__(self):
        return str(self)

    def get_name(self):
        return self.cmd_name


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
        found = re.search(self.pattern, cmd)
        arg_number = len(self.arg_names)
        args = {}
        for i in range(arg_number):
            group_number = i + 1  # Offset by 1 because group 0 is the whole string
            args[self.arg_names[i]] = found.group(group_number)
        return Command(self.cmd_name, args)


class CommandProcessor:

    def __init__(self):
        self.commands = ['roll', 'clear', 'color', 'refresh', 'choice']
        self.shortcuts = {}
        self.handlers = {
            'roll': RegexCommandHandler('roll', ['no_of_dice', 'die_type', 'mod'],
                                        r'(\d*)?\s*(d[\d\w]*)\s*([+-]\s*\d*)?'),
            'clear': CommandHandler('clear'),

            'color': RegexCommandHandler('color', ['color', 'text'],
                                         r'([a-z]*)\s*["\'](.*)["\']$'),
            'refresh': CommandHandler('refresh'),

            'choice': RegexCommandHandler('choice', ['list_of_users', 'choice_text', 'options'],
                                          '(@.*\S)? *"(.*)"\s*"(.*)"')
        }

    def process_command(self, cmd_name, cmd):
        if cmd_name in self.commands:
            cmd_handler = self.handlers[cmd_name]
        else:
            return None
        args = cmd_handler.parse_command(cmd)
        command = Command(cmd_name, args)
        if cmd_name == 'roll':
            dice_game.process_input(command)
        if cmd_name == 'clear':
            connection_manager = App.get_running_app().get_user_handler().get_connection_manager()
            message_factory = App.get_running_app().get_message_factory()
            message = message_factory.build_clear_message()
            connection_manager.send_msg(message)
            connection_manager.send_local(message)
        if cmd_name == 'color':
            user_handler = App.get_running_app().get_user_handler()
            user = user_handler.get_user()
            user.set_color(command['color'])
            user_handler.send_message(command['text'])
            user.set_color('normal')
        if cmd_name == 'refresh':
            return
        if cmd_name == 'choice':
            connection_manager = App.get_running_app().get_user_handler().get_connection_manager()
            message_factory = App.get_running_app().get_message_factory()
            message = message_factory.build_choice_message(command['choice_text'], command['options'], command['list_of_users'])
            connection_manager.send_msg(message)
            #######################################
            connection_manager.send_local(message)

    def load_shortcuts(self):
        self.shortcuts = {}
        config = App.get_running_app().config
        for shortcut in config.items('command_shortcuts'):
            self.shortcuts[shortcut[0]] = shortcut[1]
        
            

command_processor = CommandProcessor()
