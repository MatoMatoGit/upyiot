# A simple HTTP server that only accept GET request
# It adopt the programming style of ESP8266WebServer 
# library in ESP8266 Arduino Core

import network
import machine
import socket
import uselect
import os
from lib import Log

class WebServer:
    
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Use for checking a new client connection
        self.poller = uselect.poll()
        # Dict for registed handlers of all paths
        self.handlers = {}
        # The path to the web documents on MicroPython filesystem
        self.docPath = "/"
        
        self.Log = Log.Log("WebServer", True)

    # Function to start http server
    def begin(self, port):
        ip = '0.0.0.0'
        self.server.bind((ip, port))
        self.server.listen(1)
        self.Log.Print("Started listening at {}:{}".format(ip, port))
        
        # Register for checking new client connection
        self.poller.register(self.server, uselect.POLLIN)


    def close(self):
        self.poller.unregister(self.server)
        self.server.close()
        self.Log.Print("Stopped listening")


    # Check for new client connection and process the request
    def handleClient(self):
        # Note:don't call poll() with 0, that would randomly cause
        # reset with "Fatal exception 28(LoadProhibitedCause)" message
        self.Log.Print("Polling for client connection")
        res = self.poller.poll(100)
        if res:  # There's a new client connection
            self.Log.Print("Client connection found.")
            (socket, sockaddr) = self.server.accept()
            self.handle(socket)
            socket.close()


    # Response error message to client
    def err(self, socket, code, message):
        socket.write("HTTP/1.1 " + code + " " + message + "\r\n\r\n")
        socket.write("<h1>" + message + "</h1>")
        self.Log.Print("Sent response: Err ({}-{}).".format(code, message))


    # Response successful message to client
    def ok(self, socket, code, msg):
        socket.write("HTTP/1.1 " + code + " OK\r\n\r\n")
        socket.write(msg)
        self.Log.Print("Sent response: OK.")


    # Processing new GET request
    def handle(self, socket):
        self.Log.Print("Handling client request.")
        currLine = str(socket.readline(), 'utf-8')
        request = currLine.split(" ")
        if len(request) != 3:  # Discarded if it's a bad header
            self.Log.Print("Bad request header.")
            return
        (method, url, version) = request
        if "?" in url:  # Check if there's query string?
            self.Log.Print("Received query.")
            (path, query) = url.split("?", 2)
        else:
            (path, query) = (url, "")
        args = {}
        if query:  # Parsing the querying string
            argPairs = query.split("&")
            for argPair in argPairs:
                arg = argPair.split("=")
                args[arg[0]] = arg[1]
        while True:  # Read until blank line after header
            header = socket.readline()
            if header == b"":
                return
            if header == b"\r\n":
                break
    
        # Check for supported HTTP version
        if version != "HTTP/1.0\r\n" and version != "HTTP/1.1\r\n":
            self.err(socket, "505", "Version Not Supported")
        elif method == "GET":  # Only accept GET request
            if path.find(self.docPath) == 0:  # Check for path to any document
                try:
                    os.stat(path)  # Check for file existence
                    # Response header first
                    socket.write("HTTP/1.1 200 OK\r\n\r\n")
                    # Response the file content
                    f = open(path, "rb")
                    while True:
                        data = f.read(64)
                        if (data == b""):
                            break
                        socket.write(data)
                        return
                except:  # Can't find the file specified in path
                    self.err(socket, "404", "Not Found")
            elif path in self.handlers:  # Check for registered path
                self.handlers[path](socket, args)
            else:
                self.err(socket, "400", "Bad Request")
        else:
            self.err(socket, "501", "Not Implemented")
    
    # Register handler for processing request of specified path
    def onPath(self, path, handler):
        self.handlers[path] = handler
    
    
    # Set the path to documents' directory
    def setDocPath(self, path):
        self.docPath = path

