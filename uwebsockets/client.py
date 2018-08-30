"""
Websockets client for micropython

Based very heavily off
https://github.com/aaugustin/websockets/blob/master/websockets/client.py
"""

#import logging
import usocket as socket
import ubinascii as binascii
import urandom as random

from .protocol import Websocket, urlparse, readline

#LOGGER = logging.getLogger(__name__)
class LOGGER:
    @classmethod
    def debug(self, *args, **kwargs):
        print(*args)



class WebsocketClient(Websocket):
    is_client = True


def connect(uri):
    """
    Connect a websocket.
    """

    uri = urlparse(uri)
    assert uri

    if __debug__: LOGGER.debug("open connection %s:%s",
                                uri.hostname, uri.port)

    sock = socket.socket()
    LOGGER.debug("got a socket")
    try:
        addr = socket.getaddrinfo(uri.hostname, uri.port)
        LOGGER.debug("getaddrinfo result")
        LOGGER.debug(addr)
        sock.connect(addr[0][4])
        LOGGER.debug("connected using getaddrinfo method")
    except OSError:
        sock.connect((uri.hostname, int(uri.port)))
        LOGGER.debug("connected using direct method")

    def send_header(header, *args):
        if __debug__: LOGGER.debug(str(header), *args)
        sock.send(header % args + '\r\n')

    # Sec-WebSocket-Key is 16 bytes of random base64 encoded
    key = binascii.b2a_base64(bytes(random.getrandbits(8)
                                    for _ in range(16)))[:-1]
    LOGGER.debug("set key to:")
    LOGGER.debug(key)

    send_header(b'GET %s HTTP/1.1', uri.path or '/')
    send_header(b'Host: %s:%s', uri.hostname, uri.port)
    send_header(b'Connection: Upgrade')
    send_header(b'Upgrade: websocket')
    send_header(b'Sec-WebSocket-Key: %s', key)
    send_header(b'Sec-WebSocket-Version: 13')
    send_header(b'Origin: http://localhost')
    send_header(b'')

    header = readline(sock)
    assert header == b'HTTP/1.1 101 Switching Protocols', header

    # We don't (currently) need these headers
    # FIXME: should we check the return key?
    while header:
        if __debug__: LOGGER.debug(str(header))
        header = readline(sock)

    return WebsocketClient(sock)
