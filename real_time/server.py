import signal
import asyncio

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.iostream import StreamClosedError
from tornado.tcpserver import TCPServer
from tornado.platform.asyncio import AsyncIOMainLoop, to_asyncio_future
import aioredis


class ClientConnection(object):
    """
    This class represents single socket connection. Socket listening works in
    parallel with Redis channel updates listening.
    """
    message_separator = b'\r\n'

    def __init__(self, stream):
        self._stream = stream

    @gen.coroutine
    def run(self):
        """
        Main connection loop. Launches listen on given channel and keeps
        reading data from socket until it is closed.
        """
        try:
            while True:
                try:
                    request = yield self._stream.read_until(
                        self.message_separator)
                    request_body = request.rstrip(self.message_separator)
                except StreamClosedError:
                    self._stream.close(exc_info=True)
                    return
                else:
                    response_body = request_body
                    response = response_body + self.message_separator
                    try:
                        yield self._stream.write(response)
                    except StreamClosedError:
                        self._stream.close(exc_info=True)
                        return
        except Exception as e:
            if not isinstance(e, gen.Return):
                print("Connection loop has experienced an error.")
            else:
                print('Closing connection loop because socket was closed.')

    @gen.coroutine
    def update(self, message):
        """
        Handle updates and send data if necessary.

        :param message: variable that represents the update message
        """
        response = message + self.message_separator
        try:
            yield self._stream.write(response)
        except StreamClosedError:
            self._stream.close(exc_info=True)
            return


class Server(TCPServer):
    """
    This is a TCP Server that listens to clients and handles their requests
    made using socket and also listens to specified Redis ``channel`` and
    handles updates on that channel.
    """
    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self._redis = None
        self._channel = None
        self._connections = []

    @asyncio.coroutine
    def subscribe(self, channel_name):
        """
        Create async redis client and subscribe to the given PUB/SUB channel.
        Listen to the messages and launch publish handler.

        :param channel_name: string representing Redis PUB/SUB channel name
        """
        self._redis = yield aioredis.create_redis(('localhost', 6379))
        channels = yield self._redis.subscribe(channel_name)
        print('Subscribed to "{}" Redis channel.'.format(channel_name))
        self._channel = channels[0]
        yield self.listen_redis()

    @gen.coroutine
    def listen_redis(self):
        """
        Listen to the messages from the subscribed Redis channel and launch
        publish handler.
        """
        while True:
            yield self._channel.wait_message()
            try:
                msg = yield self._channel.get(encoding='utf-8')
            except aioredis.errors.ChannelClosedError:
                print("Redis channel was closed. Stopped listening.")
                return
            if msg:
                body_utf8 = msg.encode('utf-8')
                yield [con.update(body_utf8) for con in self._connections]
            print("Message in {}: {}".format(self._channel.name, msg))

    @gen.coroutine
    def handle_stream(self, stream, address):
        print('New request has come from our {} buddy...'.format(address))
        connection = ClientConnection(stream)
        self._connections.append(connection)
        yield connection.run()
        self._connections.remove(connection)

    @gen.coroutine
    def shutdown(self):
        super(Server, self).stop()
        yield self._redis.unsubscribe(self._channel)
        yield self._redis.quit()
        self.io_loop.stop()


if __name__ == '__main__':
    def sig_handler(sig, frame):
        print('Caught signal: {}'.format(sig))
        IOLoop.current().add_callback_from_signal(server.shutdown)

    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    AsyncIOMainLoop().install()
    server = Server()
    server.listen(5567)
    IOLoop.current().spawn_callback(server.subscribe, 'updates')

    print('Starting the server...')
    asyncio.get_event_loop().run_forever()
    print('Server has shut down.')
