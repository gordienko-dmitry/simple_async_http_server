from optparse import OptionParser
import logging
import socket
import multiprocessing
import select
import logic


OK = 200
NOT_FOUND = 404
FORBIDDEN = 403
BAD_METHOD = 405
TEXTS = {
    OK: "OK",
    NOT_FOUND: "Not Found",
    FORBIDDEN: "Forbidden",
    BAD_METHOD: "Method Not Allowed"
}

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'


class AsyncServer(object):
    def __init__(self, host="localhost", port=8080, document_root="./"):
        self.host = host
        self.port = port
        self.document_root = document_root
        self._connections = {}
        self._requests = {}
        self._responses = {}

    @staticmethod
    def _headers_body_to_package_(tuple_data):
        response = "HTTP/1.0 {} {}\r\n".format(tuple_data.status, TEXTS[tuple_data.status])
        for header, value in tuple_data.headers.items():
            response += "{}: {}\r\n".format(header, value)
        response += "\r\n"

        logging.info("url for response {}".format(response))

        sent_data = response.encode("UTF-8")
        if tuple_data.method == "GET":
            sent_data += tuple_data.body
        return sent_data

    def _get_response_(self, request):
        tuple_data = logic.get_response(request, self.document_root)
        return self._headers_body_to_package_(tuple_data)

    def run_event_loop(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        server_socket.setblocking(0)
        logging.info("Starting process at %s" % self.port)

        epoll = select.epoll()
        epoll.register(server_socket.fileno(), select.EPOLLIN | select.EPOLLET)

        try:
            while True:
                events = epoll.poll(1)
                for fileno, event in events:
                    if fileno == server_socket.fileno():
                        try:
                            while True:
                                connection, address = server_socket.accept()
                                connection.setblocking( 0)
                                epoll.register(connection.fileno(), select.EPOLLIN | select.EPOLLET)
                                self._connections[connection.fileno()] = connection
                                self._requests[connection.fileno()] = b''
                                self._responses[connection.fileno()] = b''
                        except socket.error:
                            pass
                    elif event & select.EPOLLIN:
                        try:
                            while True:
                                r = self._connections[fileno].recv(1024)
                                if not r:
                                    raise socket.error
                                self._requests[fileno] += r
                        except socket.error:
                            pass
                        if EOL1 in self._requests[fileno] or EOL2 in self._requests[fileno]:
                            self._responses[fileno] = self._get_response_(self._requests[fileno])
                            epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
                            logging.info("from {} recieve package {}".format(fileno, self._requests[fileno][:250]))

                    elif event & select.EPOLLOUT:
                        try:
                            while len(self._responses[fileno]) > 0:
                                byteswritten = self._connections[fileno].send(self._responses[fileno])
                                self._responses[fileno] = self._responses[fileno][byteswritten:]                            
                        except socket.error:
                            pass
                        if len(self._responses[fileno]) == 0:
                            epoll.modify(fileno, select.EPOLLET)
                            self._connections[fileno].shutdown(socket.SHUT_RDWR)
                    elif event & select.EPOLLHUP:
                        epoll.unregister(fileno)
                        self._connections[fileno].close()
                        del self._connections[fileno]
        except Exception as e:
            logging.error("Error in event loop: {}".format(e))
        finally:
            epoll.unregister(server_socket.fileno())
            epoll.close()
            server_socket.close()
            logging.info("Stopped process")


def run(host, port, document_root):
    """start server"""
    server = AsyncServer(host, port, document_root)
    server.run_event_loop()


def start(host="localhost", port=8080, document_root="./", nworkers=0):
    """Starting workers"""

    nworkers = nworkers if nworkers else multiprocessing.cpu_count()
    for _ in range(nworkers):
        process = multiprocessing.Process(target=run, args=(host, port, document_root))
        process.start()


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("-w", "--nworkers", action="store", type=int, default=0)
    op.add_option("-r", "--document_root", action="store", default="./")

    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')

    start("", opts.port, opts.document_root, opts.nworkers)



