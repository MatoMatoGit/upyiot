# Create a TCP socket that can communicate over the internet.
socketObject = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
# Create a "request" string, which is how we "ask" the web server for data.
request = "GET /ks/test.html HTTP/1.1\r\nHost: www.micropython.org\r\n\r\n"
# Create a variable named "address" that stores the address and port 
# of the web server we wish to communicate with.
address = ("www.micropython.org", 80)
sockaddr = usocket.getaddrinfo('www.micropython.org', 80)[0][-1]
# Connect the socket object to the web server specified in "address".
socketObject.connect(sockaddr)
# Send the "GET" request to the MicroPython web server.  
# A "GET" request asks the server for the web page data.
bytessent = socketObject.send(request)
print("\r\nSent %d byte GET request to the web server." % bytessent)
 
print("Printing first 3 lines of server's response: \r\n")
# Single lines can be read from the socket, 
# useful for separating headers or
# reading other data line-by-line.
# Use the "readline" call to do this.  
# Calling it a few times will show the
# first few lines from the server's response.
socketObject.readline()
socketObject.readline()
socketObject.readline()
# The first 3 lines of the server's response 
# will be received and output to the terminal.
 
print("\r\nPrinting the remainder of the server's response: \r\n")
# Use a "standard" receive call, "recv", 
# to receive a specified number of
# bytes from the server, or as many bytes as are available.
# Receive and output the remainder of the page data.
socketObject.recv(512)
 
# Close the socket's current connection now that we are finished.
socketObject.close()
print("Socket closed.")