

class MessagingProtocol:

    def __init__(self, client):
        self.RecvCallback = None
        self.Client = client
        return

    def Setup(self, recv_callback, msg_mappings)
        self.RecvCallback = recv_callback
        self.MessageMappings = msg_mappings
        return

    def Send(self, msg_map, payload, size):
        pass

    def Receive(self):
        pass

    def Connect(self):
        pass

    def Disconnect(self):
        pass