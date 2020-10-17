from upyiot.comm.Messaging.Protocol.MessagingProtocol import MessagingProtocol
from upyiot.comm.Messaging.MessageExchange import MessageExchange

class LoraProtocol(MessagingProtocol):

    _Instance = None

    def __init__(self, lora_client):
        super().__init__(lora_client)
        LoraProtocol._Instance = self
        return

    def Setup(self, recv_callback, msg_mappings):
        MessagingProtocol.Setup(self, recv_callback, msg_mappings)
        # Set the MQTT message receive callback which is called when a message is received
        # on a topic.
        #self.Client.set_callback(MqttProtocol._ReceiveCallback)
        return

    def Send(self, msg_map, payload, size):
        self.Client.send_packet(payload)
        return

    def Receive(self):
        self.Client.receive_packet()
        return

    def Connect(self):
        self.Client.connect()

    def Disconnect(self):
        self.Client.disconnect()
        return