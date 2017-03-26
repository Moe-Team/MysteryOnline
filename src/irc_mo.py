import irc.client


class ChannelConnectionError(Exception):
    pass


class MessageQueue:

    def __init__(self):
        self.messages = []

    def is_empty(self):
        return self.messages == []

    def enqueue(self, msg):
        self.messages.insert(0, msg)

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
