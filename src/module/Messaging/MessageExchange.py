from micropython import const

from module.Messaging.Message import Message
from module.Messaging.MessageBuffer import MessageBuffer
from module.SystemTime import SystemTime

import utime


class MessageExchange(object):

    URL_FIELD_DEVICE_ID = "<id>"
    URL_FIELD_PRODUCT_NAME = "<pn>"

    PRODUCT_NAME = "smartsensor"

    MSG_DIRECTION_SEND = const(0)
    MSG_DIRECTION_RECV = const(1)
    MSG_DIRECTION_BOTH = const(2)

    CONNECT_RETRY_INTERVAL_SEC  = const(1)

    # Buffer sizes (number of messages).
    SEND_BUFFER_SIZE = const(1000)
    RECV_BUFFER_SIZE = const(100)
    
    MSG_MAP_TYPE        = const(0)
    MSG_MAP_SUBTYPE     = const(1)
    MSG_MAP_URL         = const(2)
    MSG_MAP_RECV_BUFFER = const(3)
    MSG_MAP_SUBSCRIBED  = const(4)

    _Instance = None

    def __init__(self, directory, mqtt_client_obj, client_id, mqtt_retries):
        MessageBuffer.Configure(directory, Message.MSG_SIZE_MAX)
        self.SendMessageBuffer = MessageBuffer('send', -1, -1,
                                               MessageExchange.SEND_BUFFER_SIZE)
        self.MessageMappings = set()
        self.MqttClient = mqtt_client_obj
        self.MqttRetries = mqtt_retries
        self.ServiceInit = False
        self.NewMessage = False

        self.Time = SystemTime.InstanceAcquire()
        Message.DeviceId(client_id)
        print("Device ID: {}".format(Message.DeviceId()))
        MessageExchange._Instance = self

    def RegisterMessageType(self, msg_type, msg_subtype, url, direction):
        # If this message can be received
        if direction is not MessageExchange.MSG_DIRECTION_SEND:
            # Create receive buffer for the messages of this type.
            recv_buffer = MessageBuffer('recv', msg_type, msg_subtype,
                                        MessageExchange.RECV_BUFFER_SIZE)
        else:
            recv_buffer = None

        if MessageExchange.URL_FIELD_DEVICE_ID in url:
            url = url.replace(MessageExchange.URL_FIELD_DEVICE_ID,
                              Message.DeviceId())
        if MessageExchange.URL_FIELD_PRODUCT_NAME in url:
            url = url.replace(MessageExchange.URL_FIELD_PRODUCT_NAME,
                              MessageExchange.PRODUCT_NAME)

        # Add the new mapping to the set of mappings.
        self.MessageMappings.add((msg_type, msg_subtype, url, recv_buffer))

    def Reset(self):
        self.SendMessageBuffer.Delete()
        for msg_map in self.MessageMappings:
            msg_buf = msg_map[MessageExchange.MSG_MAP_RECV_BUFFER]
            if msg_buf is not None:
                msg_buf.Delete()

    def Service(self):
        if self.ServiceInit is False:
            self._MqttSetup()
            self.ServiceInit = True

        msg_count = self.SendMessageBuffer.MessageCount()
        print("Messages in send-buffer: {}".format(msg_count))
        for i in range(0, msg_count):
            msg_tup = self.SendMessageBuffer.MessageGet()
            msg_map = self.MessageMapFromType(msg_tup[MessageBuffer.MSG_STRUCT_TYPE],
                                              msg_tup[MessageBuffer.MSG_STRUCT_SUBTYPE])
            if msg_map is not None:
                print("Found message map: {}".format(msg_map))
                topic = msg_map[MessageExchange.MSG_MAP_URL]
                msg_len = msg_tup[MessageBuffer.MSG_STRUCT_LEN]
                print("Publishing message on topic {}".format(topic))
                self.MqttClient.publish(topic, msg_tup[MessageBuffer.MSG_STRUCT_DATA][:msg_len])
            else:
                print("Warning: No topic defined for message type %d.%d" %
                      (msg_tup[MessageBuffer.MSG_STRUCT_TYPE],
                       msg_tup[MessageBuffer.MSG_STRUCT_SUBTYPE]))
        while True:
            # Check for any received MQTT messages. The 'message received'-callback is called if a message
            # was received.
            self.MqttClient.check_msg()
            if self.NewMessage is False:
                break
            self.NewMessage = False

    def MessagePut(self, msg_data_dict, msg_type, msg_subtype):
        print("[DataEx] Serializing message: {}".format(msg_data_dict))
        Message.Serialize(self.Time.DateTime(), msg_data_dict, msg_type, msg_subtype)
        print("[DataEx] Serialized length: {}".format(len(Message.Stream().getvalue().decode('utf-8'))))
        return self.SendMessageBuffer.MessagePutWithType(msg_type, msg_subtype,
                                                         Message.Stream().getvalue().decode('utf-8'))

    def MessageGet(self, msg_type, msg_subtype):
        msg_map = self.MessageMapFromType(msg_type, msg_subtype)
        print("Found message map: {}".format(msg_map))
        if msg_map is not None:
            msg_buf = msg_map[MessageExchange.MSG_MAP_RECV_BUFFER]
            if msg_buf is not None:
                msg_tup = msg_buf.MessageGet()
                if msg_tup is not None:
                    msg_len = msg_tup[MessageBuffer.MSG_STRUCT_LEN]
                    return Message.Deserialize(msg_tup[MessageBuffer.MSG_STRUCT_DATA][:msg_len])
                else:
                    print("Info: No message of type %d.%d received." % (msg_type, msg_subtype))
                    return -3
            else:
                print("Error: Message type %d.%d is specified as SEND." % (msg_type, msg_subtype))
                return -2
        else:
            print("Error: No message mapping for message type %d.%d" % (msg_type, msg_subtype))
        return -1

    @staticmethod
    def InstanceGet():
        return MessageExchange._Instance

    def MessageMapFromType(self, msg_type, msg_subtype):
        for msg_map in self.MessageMappings:
            if msg_map[MessageExchange.MSG_MAP_TYPE] is msg_type \
                    and msg_map[MessageExchange.MSG_MAP_SUBTYPE] is msg_subtype:
                return msg_map
            return None

    def MessageMapFromUrl(self, url):
        for msg_map in self.MessageMappings:
            if msg_map[MessageExchange.MSG_MAP_URL] == url:
                return msg_map
            return None

# #### Private methods ####

    @staticmethod
    def _MqttMsgRecvCallback(topic, msg):
        topic = topic.decode('utf-8')
        data_ex = MessageExchange.InstanceGet()

        # Get the message mapping from the topic
        msg_map = data_ex.MessageMapFromUrl(topic)
        if msg_map is not None:
            # Put the message string in the corresponding buffer.
            msg_buf = msg_map[MessageExchange.MSG_MAP_RECV_BUFFER]
            if msg_buf is not None:
                msg_buf.MessagePut(msg)
                data_ex.NewMessage = True
        else:
            print("Warning: No message mapping defined for topic %s" % topic)

    def _MqttSetup(self):
        print("[MQTT] Connecting to broker.")
        connected = False
        retries = 0
        # Try to connect to the MQTT broker, if it fails retry after the specified
        # interval.
        while connected is False and retries < self.MqttRetries:
            try:
                self.MqttClient.connect()
                connected = True
                print("[MQTT] Connected.")
            except OSError:
                retries = retries + 1
                print("[MQTT] Failed to connect to broker. Retries left %d"
                      % (self.MqttRetries - retries))
                utime.sleep(MessageExchange.CONNECT_RETRY_INTERVAL_SEC)
                continue

        # Set the MQTT message receive callback which is called when a message is received
        # on a topic.
        self.MqttClient.set_callback(MessageExchange._MqttMsgRecvCallback)

        # TODO: Move this to the Service. Must be done periodically.
        # Iterate through the available message mappings.
        for msg_map in self.MessageMappings:
            print("Found message map: {}".format(msg_map))
            # If the message mapping contains a receive buffer the message can be
            # received and must be subscribed to.
            if msg_map[MessageExchange.MSG_MAP_RECV_BUFFER] is not None:
                print("Subscribing to topic {}".format(msg_map[MessageExchange.MSG_MAP_URL]))
                # Subscribe to the message topic.
                self.MqttClient.subscribe(msg_map[MessageExchange.MSG_MAP_URL])


class Endpoint(object):

    def __init__(self):
        self.MsgEx = MessageExchange.InstanceGet()

    def MessagePut(self, msg_data_dict, msg_type, msg_subtype):
        return self.MsgEx.MessagePut(msg_data_dict, msg_type, msg_subtype)

    def MessageGet(self, msg_type, msg_subtype):
        return self.MsgEx.MessageGet(msg_type, msg_subtype)

