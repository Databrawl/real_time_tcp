from tornado import gen
from tornado.ioloop import IOLoop
from tornado.tcpclient import TCPClient


class Client(TCPClient):
    """
    This is a simple echo TCP Client
    """
    msg_separator = b'\r\n'

    @gen.coroutine
    def run(self, host, port):
        stream = yield self.connect(host, port)
        while True:
            data = input(">> ").encode('utf8')
            data += self.msg_separator
            if not data:
                break
            else:
                yield stream.write(data)
            data = yield stream.read_until(self.msg_separator)
            body = data.rstrip(self.msg_separator)
            print(body)


if __name__ == '__main__':
    Client().run('localhost', 5567)
    print('Connecting to server socket...')
    IOLoop.instance().start()
    print('Socket has been closed.')
