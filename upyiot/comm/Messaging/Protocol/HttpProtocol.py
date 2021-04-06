from upyiot.comm.Messaging.Protocol.MessagingProtocol import MessagingProtocol
from upyiot.comm.Messaging.MessageExchange import MessageExchange
from micropython import const
import urequests


class HttpProtocol(MessagingProtocol):

    HTTP_MTU = const(1400)

    _Instance = None

    def __init__(self):
        # TODO: Add logging
        super().__init__(None, self.HTTP_MTU)
        HttpProtocol._Instance = self
        return

    def Setup(self, recv_callback, msg_mappings):
        MessagingProtocol.Setup(self, recv_callback, msg_mappings)
        return

    def Send(self, msg_map, payload, size):
        urequests.post(msg_map[MessageExchange.MSG_MAP_ROUTING], data=payload)
        return

    def Receive(self):
        for msg_map in self.MessageMappings:
            resp = urequests.get(msg_map[MessageExchange.MSG_MAP_ROUTING])
            if resp.status_code > 200:
                self.RecvCallback(resp.content,
                                  msg_map[MessageExchange.MSG_MAP_ROUTING])
            # TODO: Add error handling.
        return

    def Connect(self):
        pass

    def Disconnect(self):
        pass
