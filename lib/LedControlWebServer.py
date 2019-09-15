from lib import WebServer
import network
import machine
import uasyncio
from lib import Led

class LedControlWebServer:

    # HTML content for "/"
    rootPage = """\
      <!DOCTYPE html>
      <head>
        <meta charset='UTF-8'>
      </head>
      <title>{0}</title>
      <body>
        {0}Status：<span style='color:{1}'>{2}</span><br>
        <a href='/cmd?led={3}'>{4}</a><br>
        <a href='/'>HOME</a>
      </body>
      </html>
      """

    def RunLoop(self):
        try:
            while True:
                # Let server process requests
                self.web_srv.handleClient()
        except:
            self.web_srv.close()
    
    # Handler for path "/" 
    def handleRoot(self, socket, args):
        global rootPage
        # Replacing title text and display text color according 
        # to the status of LED
        response = rootPage.format(
            "Remote LED", 
            "red" if self.led.State() else "green",
            "Off" if self.led.State() else "On",
            "on" if self.led.State() else "off",
            "Turn on" if self.led.State() else "Turn off"
        )
        # Return the HTML page
        self.web_srv.ok(socket, "200", response)

    # Handler for path "/cmd?led=[on|off]"    
    def handleCmd(self, socket, args):
        if 'led' in args:
            if args['led'] == 'on':
                self.led.Off()
            elif args['led'] == 'off':
                self.led.On()
            self.handleRoot(socket, args)
        else:
            self.web_srv.err(socket, "400", "Bad Request")

    # handler for path "/switch" 
    def handleSwitch(self, socket, args):
        self.led.Toggle()
        self.web_srv.ok(
            socket, 
            "200", 
            "On" if self.led.State() == 0 else "Off")



    def __init__(self, led_pin):
        self.led = Led.Led(led_pin, True)
        self.led.Off()
        
        self.web_srv = WebServer.WebServer()
        # Start the server @ port 8899
        self.web_srv.begin(80)
        
        # Register handler for each path
        self.web_srv.onPath("/", self.handleRoot)
        self.web_srv.onPath("/cmd", self.handleCmd)
        self.web_srv.onPath("/switch", self.handleSwitch)
        
        # Setting the path to documents
        self.web_srv.setDocPath("/www")
