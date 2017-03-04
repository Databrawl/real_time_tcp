from concurrent.futures import ThreadPoolExecutor

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.iostream import StreamClosedError
from tornado.tcpclient import TCPClient


class Client(TCPClient):
    """
    TCP Client that simultaneously reads from and writes to the socket.
    """
    msg_separator = b'\r\n'

    def __init__(self):
        super(Client, self).__init__()
        self._stream = None
        self._executor = ThreadPoolExecutor(1)

    @gen.coroutine
    def run(self, host, port):
        self._stream = yield self.connect(host, port)
        yield [self.read(), self.write()]

    @gen.coroutine
    def read(self):
        while True:
            try:
                data = yield self._stream.read_until(self.msg_separator)
                body = data.rstrip(self.msg_separator)
                print(body)
            except StreamClosedError:
                self.disconnect()
                return

    @gen.coroutine
    def write(self):
        while True:
            try:
                data = yield self._executor.submit(input)
                if data == 'EXIT':
                    self.disconnect()
                    return
                encoded_data = data.encode('utf8')
                encoded_data += self.msg_separator
                if not encoded_data:
                    break
                else:
                    yield self._stream.write(encoded_data)
            except StreamClosedError:
                self.disconnect()
                return

    def disconnect(self):
        super(Client, self).close()
        self._executor.shutdown(False)
        if not self._stream.closed():
            print('Disconnecting...')
            self._stream.close()


@gen.coroutine
def main():
    print('Connecting to the server socket...')
    yield Client().run('localhost', 5567)
    print('Disconnected from server socket.')


if __name__ == '__main__':
    IOLoop.instance().run_sync(main)
