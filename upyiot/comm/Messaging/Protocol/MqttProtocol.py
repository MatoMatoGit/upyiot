from upyiot.comm.Messaging.Protocol.MessagingProtocol import MessagingProtocol
from upyiot.comm.Messaging.MessageExchange import MessageExchange

class MqttProtocol(MessagingProtocol):

    _Instance = None

    def __init__(self, mqtt_client):
        super().__init__(mqtt_client)
        MqttProtocol._Instance = self
        return

    def Setup(self, recv_callback, msg_mappings):
        MessagingProtocol.Setup(self, recv_callback, msg_mappings)
        # Set the MQTT message receive callback which is called when a message is received
        # on a topic.
        self.Client.set_callback(MqttProtocol._ReceiveCallback)
        return

    def Send(self, msg_map, payload, size):
        topic = msg_map[MessageExchange.MSG_MAP_ROUTING]
        self.Client.publish(topic, payload)
        return

    def Receive(self):
        # Check for any received MQTT messages.
        self.Client.check_msg()
        return

    def Connect(self):
        self.Client.connect()

        # Subscribe to all receive topics. Only excecuted if
        # connect succeeds.
        self._SubscribeToTopics()

    def Disconnect(self):
        self.Client.disconnect()
        return

    @staticmethod
    def _ReceiveCallback(topic, message):
        print("[MqttProto] Received message")
        MqttProtocol._Instance.RecvCallback(topic, message)

    def _SubscribeToTopics(self):
        # TODO: Check what happens if subscribed twice, possible to check if already subscribed?
        # Iterate through the available message mappings.
        for msg_map in self.MessageMappings:
            print("[MqttProto] Found message map: {}".format(msg_map))
            # If the message mapping contains a receive buffer the message can be
            # received and must be subscribed to.
            if msg_map[MessageExchange.MSG_MAP_RECV_BUFFER] is not None:
                print("[MqttProto] Subscribing to topic {}".format(msg_map[MessageExchange.MSG_MAP_ROUTING]))
                # Subscribe to the message topic.
                self.Client.subscribe(msg_map[MessageExchange.MSG_MAP_ROUTING])