from upyiot.system.Service.Service import Service
from upyiot.system.Service.Service import ServiceException
from upyiot.system.Service.Service import ServiceExceptionSuspend
try:
    import usocket as socket
except:
    import socket
import uerrno


class WebserverExceptionInternalError(ServiceException):

    def __init__(self):
        super().__init__()


class WebserverService(Service):

    WEBSERVER_SERVICE_MODE = Service.MODE_RUN_PERIODIC

    def __init__(self):
        super().__init__("WebSrv", self.WEBSERVER_SERVICE_MODE, {})


class Webserver(WebserverService):

    QUERY_SEPARATORS = ('&', '/')
    QUERY_VALUE      = '='

    def __init__(self, web_page_html, timeout_sec):
        # Initialize the WebserverService class.
        super().__init__()

        self.Socket = None
        self.Html = web_page_html
        self.Queries = {}
        self.TimeoutSec = timeout_sec
        print(self.Html)
        return

    def UpdatePage(self, html):
        self.Html = html

    def RegisterQueryHandle(self, query, handle, context):
        self.Queries[query] = (handle, context)

    def SvcInit(self):
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        print(addr)
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.Socket.settimeout(self.TimeoutSec)
        self.Socket.bind(addr)
        print(self.Socket)
        # try:
        #     s.bind('0.0.0.0')
        # except socket.error as msg:
        #     print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        self.Socket.listen(1)

    def SvcRun(self):
        try:
            conn, addr = self.Socket.accept()
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024)

            print('Content = %s' % request)
            query = self._QueryFromRequest(request)
            print(query)

            response = self.Html
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()

            self._QueryDispatch(query)
        except OSError as e:
            if e.args[0] is uerrno.ETIMEDOUT:
                print("[WebSrv] No connection accepted.")
                raise ServiceExceptionSuspend
            else:
                print("[WebSrv] An error occurred.")
                raise WebserverExceptionInternalError

    def _QueryFromRequest(self, request):
        query_start = request.find(b'?')
        if query_start > 0:
            query_end = request.find(b' ', query_start)
            if query_end > 0:
                query = request[query_start:query_end].decode('utf-8')
                print("Found query: {}".format(query))
                return query
        return ""

    def _QueryDispatch(self, query):
        if query == "":
            return

        for q in self.Queries.keys():
            rel_pos = query.find(q)
            # Find the registered query in the received query.
            if rel_pos > 0:
                print("Found {}".format(q))
                # Find the value position.
                pos_start = query[rel_pos:].find(Webserver.QUERY_VALUE)
                # If not value is found, continue.
                if pos_start < 0:
                    continue
                # Add the relative position.
                pos_start += rel_pos
                # Add 1 for the QUERY_VALUE character.
                pos_start += 1
                print("Start pos: {}".format(pos_start))
                # Find the value end position by looking through
                # possible separators.
                # Note that the query is spliced at the value start.
                for sep in Webserver.QUERY_SEPARATORS:
                    print("Finding {} in {}".format(sep, query[pos_start:]))
                    pos_end = query[pos_start:].find(sep)
                    # Found a separator
                    if pos_end > 0:
                        break
                print("End pos: {}".format(pos_end))
                # If the end position was found, splice the query from start until
                # end.
                if pos_end > 0:
                    value = query[pos_start:pos_end+pos_start]
                else:
                    # Splice the query from start until the end of the query.
                    value = query[pos_start:]
                # Call the registered handler with the query-value.
                self.Queries[q][0](self.Queries[q][1], q, value)

