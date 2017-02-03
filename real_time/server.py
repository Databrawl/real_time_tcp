from tornado import gen
from tornado.iostream import StreamClosedError
from tornado.tcpserver import TCPServer


class Protocol:
    """
    Class that defines basic Business Logic operations for
    interaction with client in a specific environment.
    """
    def handle_request(self, data):
        """
        This function takes data obtained from client and handles it
        appropriately
        :param data (str): data from client
        :return (str) data to be sent to the client as a response
        """
        pass


class Server(TCPServer):
    """
    This is a TCP Server that listens to clients and handles their requests
    based on the Protocol specified.
    """
    message_separator = '\r\n'

    def __init__(self, protocol, *args, **kwargs):
        self.protocol = protocol
        self._connections = []
        super(Server, self).__init__(*args, **kwargs)

    def handle_stream(self, stream, address):
        """
        Main connection loop. Launches listen on given channel and keeps
        reading data from socket until it is closed.
        """
        try:
            while True:
                try:
                    request = yield stream.read_until(self.message_separator)
                    request_body = request.rstrip(self.message_separator)
                except StreamClosedError:
                    stream.close(exc_info=True)
                    raise gen.Return()
                else:
                    response_body = self.protocol.handle_request(request_body)
                    response = response_body + self.message_separator
                    try:
                        yield stream.write(response)
                    except StreamClosedError:
                        stream.close(exc_info=True)
                        raise gen.Return()
        except Exception as e:
            if not isinstance(e, gen.Return):
                print("Connection loop has experienced an error.")


if __name__ == '__main__':
    server = Server(Protocol())
