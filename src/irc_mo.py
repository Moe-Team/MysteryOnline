import irc.client
from mopopup import MOPopup
from kivy.uix.textinput import TextInput
from kivy.app import App


class ChannelConnectionError(Exception):
    pass


class Message:
    """This class will eventually handle message parsing and any other operations
    on messages.
    """
    def __init__(self, message, sender="default"):
        self.msg = message
        self.sender = sender

    def __str__(self):
        return self.msg

    def __repr__(self):
        return str(self.msg)

    def encode(self, loc, subloc, char, sprite, pos, col_id):
        self.msg = "{}#{}#{}#{}#{}#{}#{}".format(loc, subloc, char, sprite, pos, col_id, self.msg)

    def decode(self):
        res = self.msg.split("#", 6)
        res.insert(0, self.sender)
        return tuple(res)

    def decode_other(self):
        res = self.msg.split("#", 1)
        res.append(self.sender)
        return res[1], res[2]

    def identify(self):
        if self.msg.count('#') >= 6:
            return 'chat'
        if self.msg.startswith('c#'):
            return 'char'
        if self.msg.startswith('OOC#'):
            return 'OOC'
        if self.msg.startswith('m#'):
            return 'music'


class MessageQueue:
    """Standard First-In-First-Out queue for irc messages.
    """

    def __init__(self):
        self.messages = []

    def is_empty(self):
        return self.messages == []

    def enqueue(self, msg, sender):
        message = Message(msg, sender)
        self.messages.insert(0, message)

    def dequeue(self):
        try:
            return self.messages.pop()
        except IndexError:
            return None

    def size(self):
        return len(self.messages)


class PrivateMessage:
    def __init__(self, msg, sender="default", receiver="default"):
        self.sender = sender
        self.receiver = receiver
        self.msg = msg


class PrivateConversation:
    def __init__(self):
        self.user = ''
        self.msgs = ''


class PrivateMessageQueue:
    """Standard First-In-First-Out queue for irc messages.
    """
    def __init__(self):
        self.private_messages = []

    def enqueue(self, msg, sender):
        message = PrivateMessage(msg, sender, "no")
        self.private_messages.insert(0, message)

    def dequeue(self):
        try:
            return self.private_messages.pop()
        except IndexError:
            return None


class IrcConnection:

    def __init__(self, server, port, channel, username):
        self.reactor = irc.client.Reactor()
        self.username = username
        self.channel = channel
        self._joined = False
        self.msg_q = MessageQueue()
        self.p_msg_q = PrivateMessageQueue()
        self.on_join_handler = None
        self.on_users_handler = None
        self.on_disconnect_handler = None

        try:
            self.connection = self.reactor.server().connect(server, port, username)
        except irc.client.ServerConnectionError:
            print("Something went wrong m8")
            raise

        events = ["welcome", "join", "quit", "pubmsg", "nicknameinuse", "namreply", "privnotice", "privmsg"]
        for e in events:
            self.connection.add_global_handler(e, getattr(self, "on_" + e))

    def get_msg(self):
        return self.msg_q.dequeue()

    def get_pm(self):
        return self.p_msg_q.dequeue()

    def send_msg(self, msg, *args):
        args = tuple(args)
        message = Message(msg)
        message.encode(*args)
        self.msg_q.messages.insert(0, message)
        self.connection.privmsg(self.channel, message.msg)

    def send_private_msg(self, receiver, sender, msg):
        pm = PrivateMessage(msg, sender, receiver)
        self.p_msg_q.private_messages.insert(0, pm)
        if len(msg) > 480:  # controls the msg length so it doesn't crash
            msg = (msg[:480] + '..')
        self.connection.privmsg(receiver, msg)

    def send_special(self, kind, value):
        kinds = {'char': 'c#', 'OOC': 'OOC#', 'music': 'm#'}
        msg = kinds[kind] + value
        self.connection.privmsg(self.channel, msg)
        if kind == 'OOC':
            message = Message(msg)
            self.msg_q.messages.insert(0, message)

    def is_connected(self):
        return self._joined

    def process(self):
        self.reactor.process_once()

    def on_welcome(self, c, e):
        if irc.client.is_channel(self.channel):
            c.join(self.channel)
        else:
            raise ChannelConnectionError("Couldn't connect to {}".format(self.channel))

    def on_join(self, c, e):
        self._joined = True
        nick = e.source.nick
        if c.nickname != nick:
            self.on_join_handler(nick)

    def on_quit(self, c, e):
        nick = e.source.nick
        self.on_disconnect_handler(nick)

    def on_pubmsg(self, c, e):
        msg = e.arguments[0]
        self.msg_q.enqueue(msg, e.source.nick)

    def on_namreply(self, c, e):
        self.on_users_handler(e.arguments[2])

    def on_privnotice(self, c, e):
        print(e.arguments)

    def on_nicknameinuse(self, c, e):
        temp_pop = MOPopup("Username in use", "Username in use, pick another one.", "OK")
        text_inp = TextInput(multiline=False, size_hint=(1, 0.4))
        temp_pop.box_lay.add_widget(text_inp)

        def temp_handler(*args):
            c.nick(text_inp.text)
            App.get_running_app().get_user().username = text_inp.text
        temp_pop.bind(on_dismiss=temp_handler)
        temp_pop.open()

    def on_privmsg(self, c, e):
        msg = e.arguments[0]
        self.p_msg_q.enqueue(msg, e.source.nick)
