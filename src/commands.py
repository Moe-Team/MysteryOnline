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

    def __init__(self, cmd, args):
        self.cmd = cmd
        self.args = args

    def __getitem__(self, item):
        return self.args[item]


class CommandHandler:

    def __init__(self, cmd, form, prefix="/"):
        self.num_of_args = None
        self.cmd = cmd
        self.types = []
        self.names = []
        self.prefix = prefix
        self.parse_format(form)

    def parse_format(self, form):
        args = form.split(' ')
        self.num_of_args = len(args)
        for arg in args:
            type_, name = arg.split(':')
            self.types.append(type_)
            self.names.append(name)

    def parse_command(self, msg):
        if not msg.startswith(self.prefix):
            raise CommandPrefixNotFoundError(self.prefix, msg[0])
        args = msg.split(' ')
        args_processed = {}
        # Extract the command name without the prefix
        cmd = args[0][1:]
        for i, arg in enumerate(args[1:]):
            if self.types[i] == 'str':
                arg = str(arg)
            elif self.types[i] == 'int':
                arg = int(arg)
            elif self.types[i] == 'float':
                arg = float(arg)
            else:
                raise CommandUnknownArgumentTypeError(self.types[i])
            args_processed[self.names[i]] = arg
        command = Command(cmd, args_processed)
        return command
