import irc.client
from mopopup import MOPopup
from kivy.uix.textinput import TextInput


class ChannelConnectionError(Exception):
    pass


class Message:
    '''This class will eventually handle message parsing and any other operations
    on messages.
    '''
    def __init__(self, message):
        self.msg = message

    def __str__(self):
        return self.msg

    def __repr__(self):
        return str(self.msg)

    def encode(self, name, loc, subloc, char, sprite, pos):
        self.msg = "{}#{}#{}#{}#{}#{}#{}".format(name, loc, subloc, char, sprite, pos, self.msg)

    def decode(self):
        if self.msg.count("#") < 6:
            return False
        res = self.msg.split("#", 6)
        return tuple(res)

class MessageQueue:
    '''Standard First-In-First-Out queue for irc messages.
    '''

    def __init__(self):
        self.messages = []

    def is_empty(self):
        return self.messages == []

    def enqueue(self, msg):
        message = Message(msg)
        self.messages.insert(0, message)

    def dequeue(self):
        try:
            return self.messages.pop()
        except IndexError:
            return None

    def size(self):
        return len(self.messages)


class IrcConnection:

    def __init__(self, server, port, channel, username):
        self.reactor = irc.client.Reactor()
        self.username = username
        self.channel = channel
        self._joined = False
        self.msg_q = MessageQueue()
        self.on_join_handler = None
        self.on_users_handler = None

        try:
            self.connection = self.reactor.server().connect(server, port, username)
        except irc.client.ServerConnectionError:
            print("Something went wrong m8")
            raise

        events = ["welcome", "join", "disconnect", "pubmsg", "nicknameinuse", "namreply"]
        for e in events:
            self.connection.add_global_handler(e, getattr(self, "on_" + e))

    def get_msg(self):
        return self.msg_q.dequeue()

    def send_msg(self, msg, name, loc, subloc, char, sprite, pos):
        message = Message(msg)
        message.encode(name, loc, subloc, char, sprite, pos)
        self.connection.privmsg(self.channel, message.msg)

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
        nick = e.source.nick
        if c.nickname != nick:
            self.on_join_handler(nick)
        else:
            self._joined = True

    def on_disconnect(self, c, e):
        pass

    def on_pubmsg(self, c, e):
        msg = e.arguments[0]
        self.msg_q.enqueue(msg)
        print(msg)

    def on_namreply(self, c, e):
        self.on_users_handler(e.arguments[2])

    def on_nicknameinuse(self, c, e):
        temp_pop = MOPopup("Username in use", "Username in use, pick another one.", "OK")
        text_inp = TextInput(multiline=False, size_hint=(1, 0.4))
        temp_pop.box_lay.add_widget(text_inp)
        def temp_handler(*args):
            c.nick(text_inp.text)

        temp_pop.bind(on_dismiss=temp_handler)
        temp_pop.open()
