from upyiot.comm.Messaging.Protocol.MessagingProtocol import MessagingProtocol
from upyiot.comm.Messaging.MessageExchange import MessageExchange

class LoraProtocol(MessagingProtocol):

    _Instance = None

    def __init__(self, lora_client):
        super().__init__(lora_client)
        LoraProtocol._Instance = self
        self.FrameCounter = 0
        return

    def Setup(self, recv_callback, msg_mappings):
        MessagingProtocol.Setup(self, recv_callback, msg_mappings)
        self.Client.on_receive(LoraProtocol._ReceiveCallback)
        return

    def Send(self, msg_map, payload, size):
        self.Client.send_data(data=payload, data_length=size,
                              frame_counter=self.FrameCounter)
        self.FrameCounter += 1
        return

    def Receive(self):
        self.Client.receive()
        return

    def Connect(self):
        self.Client.connect()

    def Disconnect(self):
        self.Client.disconnect()
        return

    @staticmethod
    def _ReceiveCallback(lora, outgoing):
        payload = lora.read_payload()
        print("Received: {}".format(payload))
        LoraProtocol._Instance.RecvCallback("none", payload)

