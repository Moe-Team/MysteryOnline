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

        try:
            self.connection = self.reactor.server().connect(server, port, username)
        except irc.client.ServerConnectionError:
            print("Something went wrong m8")
            raise

        self.connection.add_global_handler("welcome", self.on_connect)
        self.connection.add_global_handler("join", self.on_join)
        self.connection.add_global_handler("disconnect", self.on_disconnect)
        self.connection.add_global_handler("pubmsg", self.on_pubmsg)
        self.connection.add_global_handler("nicknameinuse", self.on_nickname_in_use)

    def get_msg(self):
        return self.msg_q.dequeue()

    def send_msg(self, msg):
        self.connection.pubmsg(msg)

    def is_connected(self):
        return self._joined

    def process(self):
        self.reactor.process_once()

    def on_connect(self, c, e):
        if irc.client.is_channel(self.channel):
            c.join(self.channel)
        else:
            raise ChannelConnectionError("Couldn't connect to {}".format(self.channel))

    def on_join(self, c, e):
        self._joined = True

    def on_disconnect(self, c, e):
        pass

    def on_pubmsg(self, c, e):
        msg = e.arguments[0]
        self.msg_q.enqueue(msg)

    def on_nickname_in_use(self, c, e):
        temp_pop = MOPopup("Username in use", "Username in use, pick another one.", "OK")
        text_inp = TextInput(multiline=False, size_hint=(1, 0.4))
        temp_pop.box_lay.add_widget(text_inp)
        def temp_handler(*args):
            c.nick(text_inp.text)

        temp_pop.bind(on_dismiss=temp_handler)
        temp_pop.open()
