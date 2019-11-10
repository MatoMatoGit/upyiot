from upyiot.system.Service.Service import Service
try:
    import usocket as socket
except:
    import socket


class WebserverService(Service):

    WEBSERVER_SERVICE_MODE = Service.MODE_RUN_PERIODIC

    def __init__(self):
        super().__init__(self.WEBSERVER_SERVICE_MODE, ())


class Webserver(WebserverService):

    def __init__(self, web_page_html):
        # Initialize the WebserverService class.
        super().__init__()

        self.Socket = None
        self.Html = web_page_html
        self.Queries = {}
        print(self.Html)
        return

    def RegisterQueryHandle(self, query, handle):
        self.Queries[query] = handle

    def SvcInit(self):
        addr = socket.getaddrinfo('0.0.0.0', 8888)[0][-1]
        print(addr)
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.Socket.settimeout(10)
        self.Socket.bind(addr)
        print(self.Socket)
        # try:
        #     s.bind('0.0.0.0')
        # except socket.error as msg:
        #     print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        self.Socket.listen(1)

    def SvcRun(self):
        conn, addr = self.Socket.accept()
        #ss = ussl.wrap_socket(s, server_side=True, key=key, cert=cert)
        #print('Secure socket: {}'.format(ss))
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)

        print('Content = %s' % request)
        query = self._Query(request)
        print(query)

        response = self.Html
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()

        self._QueryDispatch(query)

    def _Query(self, request):
        query_start = request.find(b'?')
        if query_start > 0:
            query_end = request.find(b' ', query_start)
            if query_end > 0:
                query = request[query_start:query_end].decode('utf-8')
                print("Found query: {}".format(query))
                return query
        return ""

    def _QueryDispatch(self, query):
        if query is "":
            return

        for q in self.Queries.keys():
            pos = query.find(q)
            if pos > 0:
                self.Queries[q](query, pos)
