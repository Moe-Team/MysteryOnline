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

    def __str__(self):
        return str(self.args)

    def __repr__(self):
        return str(self)


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
        args = self.split_msg_into_args(msg)
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
