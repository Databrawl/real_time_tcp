from tornado import gen
from tornado.ioloop import IOLoop
from tornado.iostream import StreamClosedError
from tornado.tcpserver import TCPServer


class Server(TCPServer):
    """
    This is a simple echo TCP Server
    """
    message_separator = b'\r\n'

    def __init__(self, *args, **kwargs):
        self._connections = []
        super(Server, self).__init__(*args, **kwargs)

    @gen.coroutine
    def handle_stream(self, stream, address):
        """
        Main connection loop. Launches listen on given channel and keeps
        reading data from socket until it is closed.
        """
        try:
            print('New request has come from our {} buddy...'.format(address))
            while True:
                try:
                    request = yield stream.read_until(self.message_separator)
                except StreamClosedError:
                    stream.close(exc_info=True)
                    return
                else:
                    try:
                        yield stream.write(request)
                    except StreamClosedError:
                        stream.close(exc_info=True)
                        return
        except Exception as e:
            if not isinstance(e, gen.Return):
                print("Connection loop has experienced an error.")


if __name__ == '__main__':
    Server().listen(5567)
    print('Starting the server...')
    IOLoop.instance().start()
    print('Server has shut down.')
