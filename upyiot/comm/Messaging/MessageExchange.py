from micropython import const

from upyiot.comm.Messaging.MessageSpecification import MessageSpecification
from upyiot.comm.Messaging.Message import Message
from upyiot.comm.Messaging.MessageBuffer import MessageBuffer
from upyiot.system.SystemTime.SystemTime import SystemTime
from upyiot.system.Service.Service import Service
from upyiot.system.Service.Service import ServiceException
from upyiot.system.ExtLogging import ExtLogging

import utime


class MessageExchangeService(Service):
    MSG_EX_SERVICE_MODE = Service.MODE_RUN_PERIODIC

    def __init__(self):
        super().__init__(self.MSG_EX_SERVICE_MODE, ())


class MessageExchange(MessageExchangeService):

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
        # Initialize the MessageExchangeService class.
        super().__init__()

        MessageBuffer.Configure(directory, Message.MSG_SIZE_MAX)
        self.SendMessageBuffer = MessageBuffer('send', -1, -1,
                                               MessageExchange.SEND_BUFFER_SIZE)
        self.MessageMappings = set()
        self.MqttClient = mqtt_client_obj
        self.MqttRetries = mqtt_retries
        self.ServiceInit = False
        self.NewMessage = False

        self.Log = ExtLogging.LoggerGet("MsgEx")
        self.Time = SystemTime.InstanceGet()
        Message.DeviceId(client_id)
        print("[MsgEx] Device ID: {}".format(Message.DeviceId()))
        MessageExchange._Instance = self

    def RegisterMessageType(self, msg_spec_obj):
        # If this message can be received
        if msg_spec_obj.Direction is not MessageSpecification.MSG_DIRECTION_SEND:
            # Create receive buffer for the messages of this type.
            recv_buffer = MessageBuffer('recv', msg_spec_obj.Type, msg_spec_obj.Subtype,
                                        MessageExchange.RECV_BUFFER_SIZE)
        else:
            recv_buffer = None
        print("[MsgEx] Registering message specification: {}".format(msg_spec_obj))
        # Add the new mapping to the set of mappings.
        self.MessageMappings.add((msg_spec_obj.Type, msg_spec_obj.Subtype,
                                  msg_spec_obj.Url, recv_buffer))

    def Reset(self):
        self.SendMessageBuffer.Delete()
        for msg_map in self.MessageMappings:
            msg_buf = msg_map[MessageExchange.MSG_MAP_RECV_BUFFER]
            if msg_buf is not None:
                msg_buf.Delete()

    def SvcInit(self):
        self._MqttSetup()

    def SvcRun(self):
        # TODO: REMOVE
        self.Log.info("PUB")
        msg_count = self.SendMessageBuffer.MessageCount()
        print("[MsgEx] Messages in send-buffer: {}".format(msg_count))
        for i in range(0, msg_count):
            msg_tup = self.SendMessageBuffer.MessageGet()
            msg_map = self.MessageMapFromType(msg_tup[MessageBuffer.MSG_STRUCT_TYPE],
                                              msg_tup[MessageBuffer.MSG_STRUCT_SUBTYPE])
            if msg_map is not None:
                print("[MsgEx] Found message map: {}".format(msg_map))
                topic = msg_map[MessageExchange.MSG_MAP_URL]
                msg_len = msg_tup[MessageBuffer.MSG_STRUCT_LEN]
                print("[MsgEx] Publishing message on topic {}".format(topic))
                self.MqttClient.publish(topic, msg_tup[MessageBuffer.MSG_STRUCT_DATA][:msg_len])
            else:
                print("[MsgEx] Warning: No topic defined for message type %d.%d" %
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
        print("[MsgEx] Serializing message: {}".format(msg_data_dict))
        Message.Serialize(self.Time.DateTime(), msg_data_dict, msg_type, msg_subtype)
        print("[MsgEx] Serialized length: {}".format(len(Message.Stream().getvalue()))) #.decode('utf-8')
        return self.SendMessageBuffer.MessagePutWithType(msg_type, msg_subtype,
                                                         Message.Stream().getvalue()) #.decode('utf-8')

    def MessageGet(self, msg_type, msg_subtype):
        msg_map = self.MessageMapFromType(msg_type, msg_subtype)
        print("[MsgEx] Found message map: {}".format(msg_map))
        if msg_map is not None:
            msg_buf = msg_map[MessageExchange.MSG_MAP_RECV_BUFFER]
            if msg_buf is not None:
                msg_tup = msg_buf.MessageGet()
                if msg_tup is not None:
                    msg_len = msg_tup[MessageBuffer.MSG_STRUCT_LEN]
                    return Message.Deserialize(msg_tup[MessageBuffer.MSG_STRUCT_DATA][:msg_len])
                else:
                    print("[MsgEx] Info: No message of type %d.%d received." % (msg_type, msg_subtype))
                    return -3
            else:
                print("[MsgEx] Error: Message type %d.%d is specified as SEND." % (msg_type, msg_subtype))
                return -2
        else:
            print("[MsgEx] Error: No message mapping for message type %d.%d" % (msg_type, msg_subtype))
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
            print("[MsgEx] Warning: No message mapping defined for topic %s" % topic)

    def _MqttSetup(self):
        print("[MsgEx] Connecting to broker.")
        connected = False
        retries = 0
        # Try to connect to the MQTT broker, if it fails retry after the specified
        # interval.
        while connected is False and retries < self.MqttRetries:
            try:
                self.MqttClient.connect()
                connected = True
                print("[MsgEx] Connected.")
            except OSError:
                retries = retries + 1
                print("[MsgEx] Failed to connect to broker. Retries left %d"
                      % (self.MqttRetries - retries))
                utime.sleep(MessageExchange.CONNECT_RETRY_INTERVAL_SEC)
                continue

        if connected is False:
            # TODO: Raise ServiceException
            return

        # Set the MQTT message receive callback which is called when a message is received
        # on a topic.
        self.MqttClient.set_callback(MessageExchange._MqttMsgRecvCallback)

        # TODO: Move this to the SvcRun. Must be done periodically.
        # Iterate through the available message mappings.
        for msg_map in self.MessageMappings:
            print("[MsgEx] Found message map: {}".format(msg_map))
            # If the message mapping contains a receive buffer the message can be
            # received and must be subscribed to.
            if msg_map[MessageExchange.MSG_MAP_RECV_BUFFER] is not None:
                print("[MsgEx] Subscribing to topic {}".format(msg_map[MessageExchange.MSG_MAP_URL]))
                # Subscribe to the message topic.
                self.MqttClient.subscribe(msg_map[MessageExchange.MSG_MAP_URL])


class Endpoint(object):

    def __init__(self):
        self.MsgEx = MessageExchange.InstanceGet()

    def MessagePut(self, msg_data_dict, msg_type, msg_subtype):
        return self.MsgEx.MessagePut(msg_data_dict, msg_type, msg_subtype)

    def MessageGet(self, msg_type, msg_subtype):
        return self.MsgEx.MessageGet(msg_type, msg_subtype)

