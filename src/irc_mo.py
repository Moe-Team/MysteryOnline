import irc.client
from mopopup import MOPopup
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.utils import platform

from character import characters
from user import User
from choice import ChoicePopup
import re


class ChannelConnectionError(Exception):
    pass


class IncorrectMessageTypeError(Exception):
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

    def build_icon_message(self, **kwargs):
        username = kwargs.get('username', None)
        if username is not None:
            result = IconMessage(username, **kwargs)
        else:
            result = IconMessage("default", **kwargs)
        return result

    def build_character_message(self, character, link=None, version=None):
        result = CharacterMessage("default", character, link, version)
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

    def build_clear_message(self, location):
        result = ClearMessage("default", location)
        return result

    def build_choice_message(self, sender, text, options, list_of_users):
        result = ChoiceMessage(sender, text, options, list_of_users)
        return result

    def build_choice_return_message(self, sender, questioner, whisper, selected_option):
        result = ChoiceReturnMessage(sender, questioner, whisper, selected_option)
        return result

    def build_from_irc(self, irc_message, username):
        if irc_message.count('#') >= 8:
            result = ChatMessage(username)
        elif irc_message.startswith("sc#"):
            result = IconMessage(username)
        elif irc_message.startswith('c#'):
            result = CharacterMessage(username)
        elif irc_message.startswith('OOC#'):
            result = OOCMessage(username)
        elif irc_message.startswith('m#'):
            result = MusicMessage(username)
        elif irc_message.startswith('l#'):
            result = LocationMessage(username)
        elif irc_message.startswith('r#'):
            result = RollMessage(username)
        elif irc_message.startswith('i#'):
            result = ItemMessage(username)
        elif irc_message.startswith('cl#'):
            result = ClearMessage(username)
        elif irc_message.startswith('ch#'):
            result = ChoiceMessage(username)
        elif irc_message.startswith('ch2#'):
            result = ChoiceReturnMessage(username)
        else:
            result = OOCMessage(username)
        result.from_irc(irc_message)
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
        self.sfx_name = kwargs.get('sfx_name')
        self.remove_line_breaks()

    def remove_line_breaks(self):
        if self.content is None:
            return
        if '\n' in self.content or '\r' in self.content:
            self.content = self.content.replace('\n', ' ')
            self.content = self.content.replace('\r', ' ')

    def to_irc(self):
        if self.components['sfx_name'] is None:
            self.components['sfx_name'] = '0'
        msg = "{0[location]}#{0[sublocation]}#{0[character]}#{0[sprite]}#" \
              "{0[position]}#{0[color_id]}#{0[sprite_option]}#{0[sfx_name]}#{0[content]}".format(self.components)
        return msg

    def from_irc(self, message):
        arguments = tuple(message.split('#', 8))
        self.location, self.sublocation, self.character, self.sprite, self.position, \
            self.color_id, self.sprite_option, self.sfx_name, self.content = arguments
        if self.sfx_name == '0':
            self.sfx_name = None

    def execute(self, connection_manager, main_screen, user_handler):
        if main_screen.text_box.is_displaying_msg:
            connection_manager.irc_connection.put_back_msg(self)
            return
        username = self.sender
        if username == "default":
            user = App.get_running_app().get_user()
        else:
            connection_manager.reschedule_ping()
            user = main_screen.users.get(username, None)
            if user is None:
                connection_manager.on_join(username)
            try:
                user.set_from_msg(self.location, self.sublocation, self.position, self.sprite, self.character)
            except (AttributeError, KeyError) as e:
                print(e)
                return
        if self.location == user_handler.get_current_loc().name and user not in main_screen.ooc_window.muted_users:
            try:
                option = int(self.sprite_option)
            except ValueError:
                return
            user.set_sprite_option(option)
            main_screen.sprite_window.set_subloc(user.get_subloc())
            main_screen.sprite_window.set_sprite(user)
            try:
                col = user.color_ids[int(self.color_id)]
            except ValueError:
                return
            if self.sfx_name is not None:
                main_screen.text_box.play_sfx(self.sfx_name)
            main_screen.text_box.display_text(self.content, user, col, username)
            main_screen.ooc_window.update_subloc(user.username, user.subloc.name)

        if self.need_to_notify(self.content, user_handler.get_user().username):
            self.notify_user()

    def need_to_notify(self, msg, username):
        p = re.compile('@'+username+'([ ]|$)', re.I)
        if re.search(p, msg):
            return True
        return False

    def notify_user(self):
        if platform == 'win':
            import ctypes
            ctypes.windll.user32.FlashWindow(App.get_running_app().get_window_handle(), True)


class IconMessage:

    def __init__(self, sender, **kwargs):
        self.components = kwargs
        self.sender = sender
        self.content = kwargs.get('content')
        self.location = kwargs.get('location')
        self.sublocation = kwargs.get('sublocation')
        self.character = kwargs.get('character')
        self.sprite = kwargs.get('sprite')
        self.position = kwargs.get('position')
        self.sprite_option = kwargs.get('sprite_option')
        self.remove_line_breaks()

    def remove_line_breaks(self):
        if self.content is None:
            return
        if '\n' in self.content or '\r' in self.content:
            self.content = self.content.replace('\n', ' ')
            self.content = self.content.replace('\r', ' ')

    def to_irc(self):
        msg = "sc#{0[location]}#{0[sublocation]}#{0[character]}#{0[sprite]}#" \
              "{0[position]}#{0[sprite_option]}".format(self.components)
        return msg

    def from_irc(self, message):
        arguments = message.split('#', 6)
        arguments.remove("sc")
        self.location, self.sublocation, self.character, self.sprite, self.position, \
        self.sprite_option = arguments

    def execute(self, connection_manager, main_screen, user_handler):
        username = self.sender
        if username == "default":
            user = App.get_running_app().get_user()
        else:
            connection_manager.reschedule_ping()
            user = main_screen.users.get(username, None)
            if user is None:
                connection_manager.on_join(username)
        try:
            option = int(self.sprite_option)
            old_subloc = main_screen.sprite_window.subloc
            user.set_from_msg(self.location, self.sublocation, self.position, self.sprite, self.character)
            user.set_sprite_option(option)
            main_screen.sprite_window.set_sprite(user, False)
            main_screen.ooc_window.update_subloc(user.username, user.subloc.name)
            main_screen.sprite_window.display_sub(old_subloc)
        except (AttributeError, KeyError, ValueError) as e:
            print(e)
            return

class ChoiceMessage:

    def __init__(self, sender, text=None, options=None, list_of_users=None):
        if text is None:
            text = 'Text'
        if options is None:
            options = 'Options'
        if list_of_users is None:
            list_of_users = 'everyone'
        self.components = {'text': text, 'options': options, 'list_of_users': list_of_users}
        self.sender = sender
        self.text = text
        self.options = options
        self.list_of_users = list_of_users

    def to_irc(self):
        msg = "ch#{0[text]}#{0[options]}#{0[list_of_users]}".format(self.components)
        return msg

    def from_irc(self, message):
        arguments = message.split('#', 3)
        arguments.remove('ch')
        self.text, self.options, self.list_of_users = arguments

    def execute(self, connection_manager, main_screen, user_handler):
        user = user_handler.get_user()
        username = user.username
        log = main_screen.log_window
        options = re.split(r'(?<!\\);', self.options)
        try:
            user = main_screen.users[self.sender]
            if user.get_loc() is not None:
                if user.get_loc().name != user_handler.get_current_loc().name:
                    return
        except KeyError:
            pass
        self.list_of_users = self.list_of_users.replace('@', '')
        if user.has_choice_popup:
            ChoicePopup('', self.sender, self.text, options, user_handler.get_user())
        elif self.list_of_users != 'everyone':
            list_of_users = self.list_of_users.split(', ')
            if username in list_of_users:
                choice_popup = ChoicePopup('', self.sender, self.text, options, user_handler.get_user())
                choice_popup.open()
        elif username != self.sender:
            choice_popup = ChoicePopup('', self.sender, self.text, options, user_handler.get_user())
            choice_popup.open()
        log.add_entry(self.sender+' gave '+self.list_of_users+' a choice.\n')


class ChoiceReturnMessage:

    def __init__(self, sender, questioner=None, whisper=False, selected_option=None):
        self.components = {'questioner': questioner, 'whisper': whisper, 'selected_option': selected_option}
        self.questioner = questioner
        self.whisper = whisper
        self.selected_option = selected_option
        self.sender = sender

    def to_irc(self):
        msg = "ch2#{0[questioner]}#{0[whisper]}#{0[selected_option]}".format(self.components)
        return msg

    def from_irc(self, message):
        arguments = message.split('#')
        arguments.remove('ch2')
        self.questioner, self.whisper, self.selected_option = arguments

    def execute(self, connection_manager, main_screen, user_handler):
        log = main_screen.log_window
        username = user_handler.get_user().username
        if self.whisper == 'Busy':
            log.add_entry(username+" was busy and didn't receive the answer.\n")
        elif self.whisper == 'Refused':
            log.add_entry(self.sender+' refused to answer.\n')
        elif self.whisper:
            if username == self.questioner:
                log.add_entry(self.sender+' whispered "'+self.selected_option+'" to you.\n')
            else:
                log.add_entry(self.sender+' whispered the answer.\n')
        else:
            if username == self.sender:
                user_handler.send_message(self.selected_option)


class CharacterMessage:

    def __init__(self, sender, character=None, link=None, version=None):
        self.sender = sender
        self.character = character
        self.character_link = link
        self.version = version

    def to_irc(self):
        msg = "c#{0}#{1}#{2}".format(self.character, self.character_link, self.version)
        return msg

    def from_irc(self, message):
        arguments = message.split('#', 3)
        self.character = arguments[1]
        if len(arguments) > 2: #If it works...
            self.character_link = arguments[2]
        if len(arguments) > 3:
            self.version = arguments[3]
        else:
            self.version = ''

    def execute(self, connection_manager, main_screen, user_handler):
        connection_manager.update_char(main_screen, self.character, self.sender, self.character_link, self.version)


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

    def execute(self, connection_manager, main_screen, user_handler):
        username = self.sender
        loc = self.location
        if username not in main_screen.users:
            try:
                main_screen.ooc_window.delete_user('@'+username)
            except AttributeError:
                pass
            main_screen.users[username] = User(username)
            main_screen.ooc_window.add_user(main_screen.users[username])
        user = main_screen.users.get(username, None)
        if user.get_loc() is not None and user.get_loc().get_name() != loc:
            main_screen.log_window.add_entry("{} moved to {}. \n".format(user.username, loc))
        user.set_loc(loc, True)
        main_screen.ooc_window.update_loc(user.username, loc)


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
        try:
            arguments = message.split('#', 1)
            self.content = arguments[1]
        except IndexError:
            self.content = message

    def execute(self, connection_manager, main_screen, user_handler):
        main_screen.ooc_window.update_ooc(self.content, self.sender)


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
        try:
            self.url = arguments[2]
        except IndexError:
            self.url = None
        if self.url == "0":
            self.url = None

    def execute(self, connection_manager, main_screen, user_handler):
        username = self.sender
        user = main_screen.users[username]
        if user.get_loc() is not None:
            if user.get_loc().name != user_handler.get_current_loc().name:
                return
        else:
            return
        if self.track_name == "stop":
            main_screen.log_window.add_entry("{} stopped the music.\n".format(username))
            main_screen.ooc_window.music_tab.music_stop(False)
        else:
            main_screen.log_window.add_entry("{} changed the music.\n".format(username))
            main_screen.ooc_window.music_tab.on_music_play(username, self.url, send_to_all=False, track_name=
                                                           self.track_name)


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

    def execute(self, connection_manager, main_screen, user_handler):
        username = self.sender
        if username == "default":
            username = "You"
        else:
            sender = main_screen.users[username]
            if sender.get_loc().name != user_handler.get_current_loc().name:
                return
        main_screen.log_window.add_entry("{} rolled {}.\n".format(username, self.roll))


class ItemMessage:

    def __init__(self, sender, item=None):
        self.sender = sender
        self.item = item
        self.remove_line_breaks()

    def remove_line_breaks(self):
        if self.item is None:
            return
        if '\n' in self.item or '\r' in self.item:
            self.item = self.item.replace('\n', ' ')
            self.item = self.item.replace('\r', ' ')

    def to_irc(self):
        msg = "i#{0}".format(self.item)
        return msg

    def from_irc(self, message):
        arguments = message.split('#', 1)
        self.item = arguments[1]

    def execute(self, connection_manager, main_screen, user_handler):
        item_string = self.item
        dcdi = item_string.split("#", 3)
        user = App.get_running_app().get_user()
        username = self.sender
        entry_text = ''
        if username != 'default':
            sender = main_screen.users[username]
            if sender.get_loc().name != user_handler.get_current_loc().name:
                return
            entry_text = ' and it was added to your inventory'
        if username == 'default':
            username = 'You'
        user.inventory.receive_item(dcdi[0], dcdi[1], dcdi[2], dcdi[3])
        main_screen.log_window.add_entry("{} presented {}{}.\n".format(username, dcdi[0], entry_text))


class ClearMessage:

    def __init__(self, sender, location=None):
        self.sender = sender
        self.location = location

    def to_irc(self):
        msg = "cl#{0}".format(self.location)
        return msg

    def from_irc(self, message):
        arguments = message.split('#', 1)
        self.location = arguments[1]

    def execute(self, connection_manager, main_screen, user_handler):
        # TODO Make it work only for the person who is currently speaking
        loc = self.location
        try:
            if loc == user_handler.get_current_loc().name:
                textbox = main_screen.text_box
                textbox.clear_textbox()
        except TypeError:
            return None


class MessageQueue:
    """Standard First-In-First-Out queue for irc messages.
    """

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
        if '\n' in msg:
            messages = msg.splitlines()
            new_msg = ""
            for m in messages:
                new_msg = new_msg + m
            self.connection.privmsg(self.channel, new_msg)
            return
        self.connection.privmsg(self.channel, msg)

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
        message_factory = App.get_running_app().get_message_factory()
        try:
            message = message_factory.build_from_irc(msg, e.source.nick)
        except IncorrectMessageTypeError:
            return
        self.msg_q.enqueue(message)

    def on_namreply(self, c, e):
        self.on_users_handler(e.arguments[2])

    def on_privnotice(self, c, e):
        server_response = e.arguments[0]
        Logger.info('IRC: {}'.format(server_response))

    def on_nicknameinuse(self, c, e):
        if len(App.get_running_app().get_user().username) < 16:
            c.nick(App.get_running_app().get_user().username + '_')
            App.get_running_app().get_user().username += '_'
            return
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
        self.not_again_flag = False
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
        if self.not_again_flag is False:
            self.ping_event.cancel()
            popup = MOPopup("Disconnected", "Seems you might be disconnected from IRC :(", "Okay.")
            popup.create_button("Don't show this again", False, btn_command=self.set_flag())
            popup.size = 800 / 2, 600 / 3
            popup.pos_hint = {'top': 1}
            popup.background_color = [0, 0, 0, 0]
            popup.open()
            # TODO Implement reconnection strategy

    def set_flag(self):
        self.not_again_flag = not self.not_again_flag

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
        self.irc_connection.msg_q.enqueue(msg)

    def update_chat(self, dt):
        msg = self.irc_connection.get_msg()
        if msg is not None:
            main_scr = App.get_running_app().get_main_screen()
            user_handler = App.get_running_app().get_user_handler()
            msg.execute(self, main_scr, user_handler)

    def update_music(self, track_name, url=None):
        message_factory = App.get_running_app().get_message_factory()
        message = message_factory.build_music_message(track_name, url)
        self.send_msg(message)

    def update_char(self, main_scr, char, username, char_link, version):
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
        main_scr.add_character_to_dlc_list(char, char_link, version)

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
        char = user.get_char()
        if char is not None:
            message_factory = App.get_running_app().get_message_factory()
            char_msg = message_factory.build_character_message(char.name, char.link, char.version)
            self.send_msg(char_msg)

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
