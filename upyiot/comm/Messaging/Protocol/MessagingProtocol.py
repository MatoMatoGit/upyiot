from micropython import const


class MessagingProtocol:

    SEND_INTERVAL_DEFAULT = const(0)

    def __init__(self, client, mtu, send_interval=SEND_INTERVAL_DEFAULT):
        self.RecvCallback = None
        self.Client = client
        self.MessageMappings = None
        self.Mtu = mtu
        self.SendInterval = send_interval
        return

    def Setup(self, recv_callback, msg_mappings):
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
