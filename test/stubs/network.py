

class WLAN:

    def __init__(self):
        self.Active = False
        self.Ssid = ""
        self.Pwd = ""
        self.Connected = False
        self.Retries = 0
        return

    def ifconfig(self, cfg=None):
        return

    def active(self, state=None):
        if state is None:
            return self.Active
        self.Active = state

    def config(self, essid="", password=""):
        self.Ssid = essid
        self.Pwd = password

    def connect(self, ssid, pwd):
        if self.Retries is 0:
            self.Ssid = ssid
            self.Pwd = pwd
            self.Connected = True
        else:
            self.Retries -= 1

    def disconnect(self):
        self.Connected = False

    def isconnected(self):
        return self.Connected

    def retries_set(self, retries):
        self.Retries = retries
