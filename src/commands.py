import re


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

    def __init__(self, cmd_name, args):
        self.cmd_name = cmd_name
        self.args = args

    def __getitem__(self, item):
        return self.args[item]

    def __str__(self):
        return str(self.args)

    def __repr__(self):
        return str(self)


class CommandHandler:

    def __init__(self, cmd_name, form):
        self.num_of_args = None
        self.cmd_name = cmd_name
        self.types = []
        self.names = []
        self.parse_format(form)

    def parse_format(self, form):
        args = form.split(' ')
        self.num_of_args = len(args)
        for arg in args:
            type_, name = arg.split(':')
            self.types.append(type_)
            self.names.append(name)

    def parse_command(self, msg):
        args = self.split_msg_into_args(msg)
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

    def split_msg_into_args(self, msg):
        args = []
        mark = None
        start_index = None
        for w in msg.split(' '):
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
        self.commands = ['roll']
        self.handlers = {
            'roll': RegexCommandHandler('roll', ['no_of_dice', 'dice_type', 'mod'], r'(\d*)?\s*(d\d*)\s*([+-]\s*\d*)?')
        }

    def process_command(self, cmd_name, cmd):
        if cmd_name in self.commands:
            cmd_handler = self.handlers[cmd_name]
        else:
            return None
        args = cmd_handler.parse_command(cmd)
        return Command(cmd_name, args)
