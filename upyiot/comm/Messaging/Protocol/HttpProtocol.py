from upyiot.comm.Messaging.Protocol.MessagingProtocol import MessagingProtocol
from upyiot.comm.Messaging.MessageExchange import MessageExchange
from upyiot.system.ExtLogging import ExtLogging
from micropython import const
import urequests

Log = ExtLogging.Create("HttpProto")

class HttpProtocol(MessagingProtocol):

    HTTP_MTU = const(1400)

    _Instance = None

    def __init__(self):
        super().__init__(None, self.HTTP_MTU)
        HttpProtocol._Instance = self
        return

    def Setup(self, recv_callback, msg_mappings):
        MessagingProtocol.Setup(self, recv_callback, msg_mappings)
        return

    def Send(self, msg_map, payload, size):
        route = msg_map[MessageExchange.MSG_MAP_ROUTING]
        Log.info("POST to {}: {}".format(route, payload))
        urequests.post(msg_map[MessageExchange.MSG_MAP_ROUTING], data=payload.decode("utf-8"))
        return

    def Receive(self):
        for msg_map in self.MessageMappings:
            route = msg_map[MessageExchange.MSG_MAP_ROUTING]
            Log.info("GET from {}: {}".format(route))
            resp = urequests.get()
            if resp.status_code > 200:
                self.RecvCallback(resp.content,
                                  route)
            # TODO: Add error handling.
        return

    def Connect(self):
        pass

    def Disconnect(self):
        pass
