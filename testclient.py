from requests.exceptions import ConnectionError
from socketIO_client import SocketIO, LoggingNamespace

def on_connect():
    print('connect')

def on_disconnect():
    print('disconnect')

def on_reconnect():
    print('reconnect')

def on_aaa_response(*args):
    print('on_aaa_response', args)

socketIO = SocketIO('http://mystery-online.herokuapp.com')
socketIO.on('connect', on_connect)
socketIO.on('disconnect', on_disconnect)
socketIO.on('reconnect', on_reconnect)

print("I got this far")
socketIO.send('Hey')
