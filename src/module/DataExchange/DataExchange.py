import uasyncio
import umqtt.simple

import utime
import uerrno
from micropython import const

from Message import Message
from MessageBuffer import MessageBuffer


class DataExchange(object):

    MSG_DIRECTION_SEND = const(0)
    MSG_DIRECTION_RECV = const(1)
    MSG_DIRECTION_BOTH = const(2)

    CONNECT_RETRY_INTERVAL_SEC  = const(5)
    MSG_URL_LEN_MAX             = const(30)

    # Buffer sizes (number of messages).
    SEND_BUFFER_SIZE = const(40)
    RECV_BUFFER_SIZE = const(10)
    
    MSG_MAP_TYPE    = const(0)
    MSG_MAP_SUBTYPE = const(1)
    MSG_MAP_URL     = const(2)
    MSG_MAP_RECV_BUFFER = const(3)

    _Instance = None

    def __init__(self, directory, mqtt_client_obj, client_id, mqtt_retries):
        self.SendMessageBuffer = MessageBuffer.MessageBuffer('send', -1, -1,
                                                             DataExchange.SEND_BUFFER_SIZE)
        self.MessageMappings = set()
        self.MqttClient = mqtt_client_obj
        self.MqttRetries = mqtt_retries
        self.ServiceInit = False

        Message.DeviceId(client_id)
        MessageBuffer.Configure(directory, Message.MSG_SIZE_MAX)
        DataExchange._Instance = self

    def RegisterMessageType(self, msg_type, msg_subtype, url, direction):

        # If this message can be received
        if direction is not DataExchange.MSG_DIRECTION_SEND:
            # Create receive buffer for the messages of this type.
            recv_buffer = MessageBuffer.MessageBuffer('recv', msg_type, msg_subtype,
                                                      url, DataExchange.RECV_BUFFER_SIZE)
            # Subscribe to the message topic.
            self.MqttClient.subscribe(url)
        else:
            recv_buffer = None
        # Add the new mapping to the set of mappings.
        self.MessageMappings.add((msg_type, msg_subtype, url, recv_buffer))

    @staticmethod
    def InstanceGet():
        return DataExchange._Instance

    def _MessageMapFromType(self, msg_type, msg_subtype):
        for msg_map in self.MessageMappings:
            if msg_map[DataExchange.MSG_MAP_TYPE] is msg_type \
                    and msg_map[DataExchange.MSG_MAP_SUBTYPE] is msg_subtype:
                return msg_map
            return None

    def _MessageMapFromUrl(self, url):
        for msg_map in self.MessageMappings:
            if msg_map[DataExchange.MSG_MAP_URL] is url:
                return msg_map
            return None

    def _MqttMsgRecvCallback(self, topic, msg):
        # Get the message mapping from the topic
        msg_map = self._MessageMapFromUrl(topic)
        if msg_map is not None:
            # Put the message string in the corresponding buffer.
            msg_buf = msg_map[DataExchange.MSG_MAP_RECV_BUFFER]
            msg_buf.MessagePut(msg)
        else:
            print("Warning: No message mapping defined for topic %s" % topic)

    def _MqttSetup(self):
        print("[MQTT] Connecting to broker.")
        connected = False
        retries = 0
        # Try to connect the MQTT broker, if it fails retry after the specified
        # interval.
        while connected is False and retries < self.MqttRetries:
            try:
                self.MqttClient.connect()
                connected = True
                print("[MQTT] Connected.")
            except OSError:
                retries = retries + 1
                print("[MQTT] Failed to connect to server. Retries left %d"
                      % (self.MqttRetries - retries))
                utime.sleep(DataExchange.CONNECT_RETRY_INTERVAL_SEC)
                continue

        # Set the MQTT message receive callback which is called when a message is received
        # on a topic.
        DataExchange.MqttClient.set_callback(DataExchange._MqttMsgRecvCallback)

    def Service(self):
        if self.ServiceInit is False:
            self._MqttSetup()
            self.ServiceInit = True

        msg_count = self.SendMessageBuffer.MessageCount()
        for i in msg_count:
            msg_struct = self.SendMessageBuffer.MessageGet()
            msg_map = self._MessageMapFromType(msg_struct[MessageBuffer.MSG_STRUCT_TYPE],
                                               msg_struct[MessageBuffer.MSG_STRUCT_SUBTYPE])
            if msg_map is not None:
                topic = msg_map[DataExchange.MSG_MAP_URL]
                self.MqttClient.publish(topic, msg_struct[MessageBuffer.MSG_STRUCT_DATA])
            else:
                print("Warning: No topic defined for message type %d.%d" %
                      (msg_struct[MessageBuffer.MSG_STRUCT_TYPE],
                       msg_struct[MessageBuffer.MSG_STRUCT_SUBTYPE]))

        # Check for any MQTT messages, the callback is called when a message
        # has arrived. If no message is pending this function check_msg will return.
        self.MqttClient.check_msg()

    def MessagePut(self, msg_data_dict, msg_type, msg_subtype):
        Message.Serialize(utime.datetime(), msg_data_dict, msg_type, msg_subtype)
        return self.SendMessageBuffer.MessagePut(Message.Stream.getvalue().decode('utf-8'))

    def MessageGet(self, msg_type, msg_subtype):
        msg_map = self._MessageMapFromType(msg_type, msg_subtype)
        if msg_map is not None:
            msg_buf = msg_map[DataExchange.MSG_MAP_RECV_BUFFER]
            return msg_buf.MessageGet()
        else:
            print("Warning: No message mapping for message type %d.%d" % (msg_type, msg_subtype))
        return -1


class Endpoint:

    def __init__(self):
        self.DataEx = DataExchange.InstanceGet()

    def MessagePut(self, msg_data_dict, msg_type, msg_subtype):
        self.DataEx.MessagePut(msg_data_dict, msg_type, msg_subtype)

    def MessageGet(self, msg_type, msg_subtype):
        return self.DataEx.MessageGet(msg_type, msg_subtype)

