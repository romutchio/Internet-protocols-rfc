import socket
import socketserver
from http.server import SimpleHTTPRequestHandler
from select import select
from time import sleep
from urllib.request import urlopen
from threading import Thread

PORT = 8080
SOCKET_TIMEOUT = 1
SOCKET_MAX_IDLE = 10


def get_blacklist(filename):
    with open(filename, 'r') as f:
        return f.read().split('\n')


def is_blacklisted(host):
    for item in BLACKLIST:
        if item in host:
            return True
    return False


class ProxyHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.socket_idle = 0
        super().__init__(request, client_address, server)

    def do_CONNECT(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            path_parts = self.path.split(':')
            host, port = path_parts[0], int(path_parts[-1])
            try:
                if is_blacklisted(host):
                    self.send_error(423)
                    return
                sock.connect((host, port))
                self.send_response(200)
                self.send_header('Proxy-agent', 'Simple HTTP proxy')
                self.end_headers()
                self.send_webpage(sock)
            except socket.error:
                self.send_error(404)
            except ConnectionError:
                pass
            finally:
                self.connection.close()

    def send_webpage(self, sock):
        socks = [self.connection, sock]
        while True:
            input_ready, output_ready, exception_ready = select(socks, [], socks, 0.1)
            if exception_ready:
                return
            if input_ready:
                for item in input_ready:
                    data = item.recv(8192)
                    if data:
                        current_sock = self.connection if item is sock else sock
                        current_sock.send(data)
                    elif self._socket_max_idle:
                        return
            elif self._socket_max_idle:
                return

    def do_GET(self):
        self.copyfile(urlopen(self.path), self.wfile)

    @property
    def _socket_max_idle(self):
        if self.socket_idle < SOCKET_MAX_IDLE:
            sleep(SOCKET_TIMEOUT)
            self.socket_idle += 1
            return False
        else:
            return True


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == '__main__':
    BLACKLIST = get_blacklist('blacklist.txt')
    print(BLACKLIST)
    server = ThreadedTCPServer(('127.0.0.1', PORT), ProxyHandler)
    thread = Thread(target=server.serve_forever)
    thread.start()