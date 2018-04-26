import irc.client
from mopopup import MOPopup
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.logger import Logger
from kivy.clock import Clock

from character import characters
from user import User


class ChannelConnectionError(Exception):
    pass


class MessageFactory:

    def __init__(self):
        pass

    def build_chat_message(self, **kwargs):
        username = kwargs.get('username', None)
        if username is not None:
            result = ChatMessage(username, **kwargs)
        else:
            result = ChatMessage("default", **kwargs)
        return result

    def build_character_message(self, character):
        result = CharacterMessage("default", character)
        return result

    def build_location_message(self, location):
        result = LocationMessage("default", location)
        return result

    def build_ooc_message(self, content):
        result = OOCMessage("default", content)
        return result

    def build_music_message(self, track_name, url):
        result = MusicMessage("default", track_name, url)
        return result

    def build_roll_message(self, roll):
        result = RollMessage("default", roll)
        return result

    def build_item_message(self, item):
        result = ItemMessage("default", item)
        return result

    def build_clear_message(self):
        result = ClearMessage("default")
        return result


class ChatMessage:

    def __init__(self, sender, **kwargs):
        # TODO Try to reduce the number of arguments
        self.components = kwargs
        self.sender = sender
        self.content = kwargs.get('content')
        self.location = kwargs.get('location')
        self.sublocation = kwargs.get('sublocation')
        self.character = kwargs.get('character')
        self.sprite = kwargs.get('sprite')
        self.position = kwargs.get('position')
        self.color_id = kwargs.get('color_id')
        self.sprite_option = kwargs.get('sprite_option')
        self.remove_line_breaks()

    def remove_line_breaks(self):
        if self.content is None:
            return
        if '\n' in self.content or '\r' in self.content:
            self.content = self.content.replace('\n', ' ')
            self.content = self.content.replace('\r', ' ')

    def to_irc(self):
        msg = "{0.location}#{0.sublocation}#{0.character}#{0.sprite}#" \
              "{0.position}#{0.color_id}#{0.sprite_option}#{0.content}".format(self.components)
        return msg

    def from_irc(self, message):
        arguments = tuple(message.split('#', len(self.components) - 1))
        self.location, self.sublocation, self.character, self.sprite, self.position, \
            self.color_id, self.sprite_option, self.content = arguments


class CharacterMessage:

    def __init__(self, sender, character=None):
        self.sender = sender
        self.character = character

    def to_irc(self):
        msg = "c#{0}".format(self.character)
        return msg

    def from_irc(self, message):
        arguments = message.split('#', 1)
        self.character = arguments[1]


class LocationMessage:

    def __init__(self, sender, location=None):
        self.sender = sender
        self.location = location

    def to_irc(self):
        msg = "l#{0}".format(self.location)
        return msg

    def from_irc(self, message):
        arguments = message.split('#', 1)
        self.location = arguments[1]


class OOCMessage:

    def __init__(self, sender, content=None):
        self.sender = sender
        self.content = content
        self.remove_line_breaks()

    def remove_line_breaks(self):
        if self.content is None:
            return
        if '\n' in self.content or '\r' in self.content:
            self.content = self.content.replace('\n', ' ')
            self.content = self.content.replace('\r', ' ')

    def to_irc(self):
        msg = "OOC#{0}".format(self.content)
        return msg

    def from_irc(self, message):
        arguments = message.split('#', 1)
        self.content = arguments[1]


class MusicMessage:

    def __init__(self, sender, track_name=None, url=None):
        self.sender = sender
        self.track_name = track_name
        self.url = url

    def to_irc(self):
        if self.track_name is None:
            self.track_name = "0"
        if self.url is None:
            self.url = "0"
        msg = "m#{0}#{1}".format(self.track_name, self.url)
        return msg

    def from_irc(self, message):
        arguments = message.split('#', 2)
        self.track_name = arguments[1]
        if self.track_name == "0":
            self.track_name = None
        self.url = arguments[2]
        if self.url == "0":
            self.url = None


class RollMessage:

    def __init__(self, sender, roll=None):
        self.sender = sender
        self.roll = roll

    def to_irc(self):
        msg = "r#{0}".format(self.roll)
        return msg

    def from_irc(self, message):
        arguments = message.split('#', 1)
        self.roll = arguments[1]


class ItemMessage:

    def __init__(self, sender, item=None):
        self.sender = sender
        self.item = item

    def to_irc(self):
        msg = "i#{0}".format(self.item)
        return msg

    def from_irc(self, message):
        arguments = message.split('#', 1)
        self.item = arguments[1]


class ClearMessage:

    def __init__(self, sender):
        self.sender = sender

    def to_irc(self):
        msg = "cl#"
        return msg


class Message:
    """This class will eventually handle message parsing and any other operations
    on messages.
    """
    def __init__(self, message, sender="default"):
        self.msg = message
        self.sender = sender
        self.remove_line_breaks()

    def remove_line_breaks(self):
        if '\n' in self.msg or '\r' in self.msg:
            self.msg = self.msg.replace('\n', ' ')
            self.msg = self.msg.replace('\r', ' ')

    def __str__(self):
        return self.msg

    def __repr__(self):
        return str(self.msg)

    def encode(self, loc, subloc, char, sprite, pos, col_id, sprite_option):
        self.msg = "{}#{}#{}#{}#{}#{}#{}#{}".format(loc, subloc, char, sprite, pos, col_id, sprite_option, self.msg)

    def decode(self):
        res = self.msg.split("#", 7)
        res.insert(0, self.sender)
        return tuple(res)

    def decode_other(self):
        res = self.msg.split("#", 1)
        res.append(self.sender)
        return res[1], res[2]

    def identify(self):
        if self.msg.count('#') >= 7:
            return 'chat'
        if self.msg.startswith('c#'):
            return 'char'
        if self.msg.startswith('OOC#'):
            return 'OOC'
        if self.msg.startswith('m#'):
            return 'music'
        if self.msg.startswith('l#'):
            return 'loc'
        if self.msg.startswith('r#'):
            return 'roll'
        if self.msg.startswith('i#'):
            return "item"
        if self.msg.startswith('cl#'):
            return "clear"

        return None


class MessageQueue:
    """Standard First-In-First-Out queue for irc messages.
    """

    def __init__(self):
        self.messages = []

    def is_empty(self):
        return self.messages == []

    def enqueue(self, msg):
        # TODO use factory here
        self.messages.insert(0, msg)

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
        self.server = server
        self.channel = channel
        self._joined = False
        self.msg_q = MessageQueue()
        self.p_msg_q = PrivateMessageQueue()
        self.on_join_handler = None
        self.on_users_handler = None
        self.on_disconnect_handler = None
        self.connection_manager = None

        try:
            self.connection = self.reactor.server().connect(self.server, port, username)
        except irc.client.ServerConnectionError:
            Logger.warning('IRC: Could not connect to server')
            raise

        events = ["welcome", "join", "quit", "pubmsg", "nicknameinuse", "namreply", "privnotice", "privmsg", "pong"]
        for e in events:
            self.connection.add_global_handler(e, getattr(self, "on_" + e))

    def set_connection_manager(self, connection_manager):
        self.connection_manager = connection_manager

    def get_msg(self):
        return self.msg_q.dequeue()

    def put_back_msg(self, msg):
        self.msg_q.messages.append(msg)

    def get_pm(self):
        return self.p_msg_q.dequeue()

    def send_msg(self, msg):
        self.connection.privmsg(self.channel, msg)

    def send_local_msg(self, msg):
        self.msg_q.messages.insert(0, msg)

    def send_private_msg(self, receiver, sender, msg):
        pm = PrivateMessage(msg, sender, receiver)
        self.p_msg_q.private_messages.insert(0, pm)
        if len(msg) > 480:  # controls the msg length so it doesn't crash
            msg = (msg[:480] + '..')
        self.connection.privmsg(receiver, msg)

    def send_mode(self, username, msg):
        self.connection.mode(username, msg)

    def send_ping(self):
        self.connection.ping(self.server)

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
        self.msg_q.enqueue(msg)

    def on_namreply(self, c, e):
        self.on_users_handler(e.arguments[2])

    def on_privnotice(self, c, e):
        server_response = e.arguments[0]
        Logger.info('IRC: {}'.format(server_response))

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

    def on_pong(self, c, e):
        self.connection_manager.receive_pong()


class ConnectionManager:

    def __init__(self, irc_connection):
        self.irc_connection = irc_connection
        self.irc_connection.set_connection_manager(self)
        self.ping_event = None
        self.disconnected_event = None
        self.reschedule_ping()

    def reschedule_ping(self):
        if self.ping_event is not None:
            self.ping_event.cancel()
        self.ping_event = Clock.schedule_interval(self.ping, 15)

    def ping(self, dt):
        try:
            self.irc_connection.send_ping()
        except irc.client.ServerNotConnectedError:
            self.get_disconnected()
        self.disconnected_event = Clock.schedule_once(self.get_disconnected, 10)

    def get_disconnected(self, *args):
        self.ping_event.cancel()
        popup = MOPopup("Disconnected", "Seems you got disconnected from IRC :(", "RIP")
        popup.bind(on_dismiss=self.close_app)
        popup.open()
        # TODO Implement reconnection strategy

    def close_app(self, *args):
        App.get_running_app().stop()

    def receive_pong(self):
        if self.disconnected_event is not None:
            self.disconnected_event.cancel()

    def send_msg(self, msg, *args):
        try:
            irc_message = msg.to_irc()
            self.irc_connection.send_msg(irc_message, *args)
        except irc.client.ServerNotConnectedError:
            self.get_disconnected()
        self.reschedule_ping()

    def send_local(self, msg):
        self.irc_connection.msg_q.insert(0, msg)

    def update_chat(self, dt):
        main_scr = App.get_running_app().get_main_screen()

        config = App.get_running_app().config
        user_handler = App.get_running_app().get_user_handler()
        msg = self.irc_connection.get_msg()
        if msg is not None:
            if msg.identify() == 'chat':
                if main_scr.text_box.is_displaying_msg:
                    self.irc_connection.put_back_msg(msg)
                    return
                self.on_chat_message(main_scr, msg, user_handler)
            elif msg.identify() == 'char':
                self.on_char_message(main_scr, msg)
            elif msg.identify() == 'loc':
                self.on_loc_message(main_scr, msg)
            elif msg.identify() == 'OOC':
                self.on_ooc_message(main_scr, msg)
            elif msg.identify() == 'music':
                self.on_music_message(main_scr, msg, user_handler)
            elif msg.identify() == 'roll':
                self.on_roll_message(main_scr, msg)
            elif msg.identify() == 'item':
                self.on_item_message(main_scr, msg, user_handler)
            elif msg.identify() == 'clear':
                self.on_clear_message(main_scr, msg)

    def on_music_message(self, main_scr, msg, user_handler):
        dcd = msg.decode_other()
        username = dcd[1]
        user = main_scr.users[username]
        if user.get_loc().name != user_handler.get_current_loc().name:
            return
        if dcd[0] == "stop":
            main_scr.log_window.add_entry("{} stopped the music.\n".format(dcd[1]))
            main_scr.ooc_window.music_tab.music_stop(False)
        else:
            main_scr.log_window.add_entry("{} changed the music.\n".format(dcd[1]))
            main_scr.ooc_window.music_tab.on_music_play(dcd[0], send_to_all=False)

    def on_ooc_message(self, main_scr, msg):
        dcd = msg.decode_other()
        main_scr.ooc_window.update_ooc(*dcd)

    def on_loc_message(self, main_scr, msg):
        dcd = msg.decode_other()
        user = dcd[1]
        loc = dcd[0]
        user = main_scr.users.get(user, None)
        if user.get_loc() is not None and user.get_loc().get_name() != loc:
            main_scr.log_window.add_entry("{} moved to {}. \n".format(user.username, loc))
        user.set_loc(loc, True)
        main_scr.ooc_window.update_loc(user.username, loc)

    def on_char_message(self, main_scr, msg):
        dcd = msg.decode_other()
        self.update_char(main_scr, *dcd)

    def on_roll_message(self, main_scr, msg):
        dcd = msg.decode_other()
        username = dcd[1]
        roll_result = dcd[0]
        if username == 'default':
            username = "You"
        main_scr.log_window.add_entry("{} rolled {}.\n".format(username, roll_result))

    def on_clear_message(self, main_scr, msg):
        # TODO Make it work only for the person who is currently speaking
        textbox = main_scr.text_box
        textbox.clear_textbox()

    def on_item_message(self, main_scr, msg, user_handler):
        dcd = msg.decode_other()
        item_string = dcd[0]
        dcdi = item_string.split("#", 3)
        user = App.get_running_app().get_user()
        username = dcd[1]
        entry_text = ''
        if username != 'default':
            sender = main_scr.users[username]
            if sender.get_loc().name != user_handler.get_current_loc().name:
                return
            entry_text = ' and it was added to your inventory'
        if username == 'default':
            username = 'You'
        user.inventory.receive_item(dcdi[0], dcdi[1], dcdi[2], dcdi[3])
        main_scr.log_window.add_entry("{} presented {}{}.\n".format(username, dcdi[0], entry_text))

    def on_chat_message(self, main_scr, msg, user_handler):
        dcd = msg.decode()
        username = dcd[0]
        if username == "default":
            user = App.get_running_app().get_user()
        else:
            self.reschedule_ping()
            user = main_scr.users.get(username, None)
            if user is None:
                self.on_join(username)
            user.set_from_msg(*dcd)
        loc = dcd[1]
        if loc == user_handler.get_current_loc().name and user not in main_scr.ooc_window.muted_users:
            option = int(dcd[7])
            sender = dcd[0]
            user.set_sprite_option(option)
            main_scr.sprite_window.set_subloc(user.get_subloc())
            main_scr.sprite_window.set_sprite(user)
            col = user.color_ids[int(dcd[6])]
            main_scr.text_box.display_text(dcd[8], user, col, sender)
            main_scr.ooc_window.update_subloc(user.username, user.subloc.name)

    def update_music(self, track_name, url=None):
        message_factory = App.get_running_app().get_message_factory()
        message = message_factory.build_music_message(track_name, url)
        self.send_msg(message)

    def update_char(self, main_scr, char, username):
        main_scr.ooc_window.update_char(username, char)
        user = App.get_running_app().get_user()
        if username == user.username:
            return
        if char not in characters:
            main_scr.users[username].set_char(characters['RedHerring'])
            main_scr.users[username].set_current_sprite('4')
        else:
            main_scr.users[username].set_char(characters[char])
        main_scr.users[username].get_char().load_without_icons()
        main_scr.users[username].remove()

    def on_join(self, username):
        main_scr = App.get_running_app().get_main_screen()
        user_handler = App.get_running_app().get_user_handler()
        user = user_handler.get_user()
        if user.username == username:
            return
        if username not in main_scr.users:
            main_scr.users[username] = User(username)
            main_scr.ooc_window.add_user(main_scr.users[username])
        main_scr.log_window.add_entry("{} has joined.\n".format(username))
        loc = user_handler.get_current_loc().name
        message_factory = App.get_running_app().get_message_factory()
        loc_message = message_factory.build_location_message(loc)
        self.send_msg(loc_message)
        self.send_local(loc_message)
        char = user.get_char()
        if char is not None:
            message_factory = App.get_running_app().get_message_factory()
            char_msg = message_factory.build_character_message(char.name)
            self.send_msg(char_msg)
            self.send_local(char_msg)

    def on_disconnect(self, username):
        main_scr = App.get_running_app().get_main_screen()
        main_scr.log_window.add_entry("{} has disconnected.\n".format(username))
        main_scr.ooc_window.delete_user(username)
        try:
            main_scr.users[username].remove()
            del main_scr.users[username]
        except KeyError:
            pass

    def on_join_users(self, users):
        main_scr = App.get_running_app().get_main_screen()
        user = App.get_running_app().get_user()
        users = users.split()
        for u in users:
            if u == "@" + user.username:
                continue
            if u != user.username:
                main_scr.users[u] = User(u)
                main_scr.ooc_window.add_user(main_scr.users[u])
