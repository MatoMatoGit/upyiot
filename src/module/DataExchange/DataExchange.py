import uasyncio
import umqtt.simple

import utime
import uerrno
import ustruct

from micropython import const

from Message import Message


class DataExchange(object):
    
    CONNECT_RETRY_INTERVAL_SEC  = const(5)
    MSG_URL_LEN_MAX             = const(30)
    
    MSG_MAP_TYPE    = const(0)
    MSG_MAP_SUBTYPE = const(1)
    MSG_MAP_URL     = const(2)

    _Instance = None
    ExchangeBuffer = bytearray(ExchangeEndpoint.MSG_DATA_LEN_MAX)

    def __init__(self, directory, mqtt_client_obj, client_id, mqtt_retries):

        self.Sources = set()
        self.Sinks = set()
        self.MessageMapping = set()
        self.MqttClient = mqtt_client_obj
        self.MqttRetries = mqtt_retries
        
        Message.DeviceId(client_id)
        ExchangeEndpoint.FileDir(directory)

        DataExchange._Instance = self
        
    def MessagePut(self, msg_data_dict, msg_type, msg_subtype):
        return 0

    def MessageGet(self, msg_type, msg_subtype):
        return 0
    
    def RegisterMessageMapping(self, msg_type, msg_subtype, url):
        self.MessageMapping.add((msg_type, msg_subtype, url))

    def UrlFromMessageType(self, msg_type, msg_subtype):
        for msg in self.MessageTypes:
            if msg[DataExchange.MSG_MAP_TYPE] is msg_type \
            and msg[DataExchange.MSG_MAP_SUBTYPE] is msg_subtype:
                return msg[DataExchange.MSG_MAP_URL]
            return None

    def MqttSetup(self):
        print("[MQTT] Connecting to server.")
        connected = False
        retries = 0
        # Try to connect the MQTT server, if it fails retry after the specified
        # interval.
        while connected is False and retries < DataExchange.MqttRetries:
            try:
                DataExchange.MqttClient.connect()
                connected = True
                print("[MQTT] Connected.")
            except OSError:
                retries = retries + 1
                print("[MQTT] Failed to connect to server. Retries left %d"
                      % (DataExchange.MqttRetries - retries))
                utime.sleep(DataExchange.CONNECT_RETRY_INTERVAL_SEC)
                continue
        # Set the MQTT callback which is called when a message arrives on a
        # topic.

        DataExchange.MqttClient.set_callback(DataExchange._MqttCallback)

    def _MqttCallback(self, topic, msg):
        # Iterate through the registered sinks and check
        # if any of them has a URL matching the topic.
        for sink in DataExchange.Sinks:
            if sink.Url is topic:
                # Dump the JSON data to a dictionary and put
                # it in the sink's queue.
                data = ujson.dump(msg)
                sink.PutNoWait(data)

    def Service(self):

        self.MqttSetup()
        if ExchangeEndpoint.SourceMessageCount() > 0:
            for msg in ExchangeEndpoint.SourceMessageFile:
                topic = self.UrlFromMessageType(msg[ExchangeEndpoint.MSG_STRUCT_TYPE],
                                           msg[ExchangeEndpoint.MSG_STRUCT_SUBTYPE])
                if topic is None:
                    print("Warning: No topic defined for message %d.%d" % (msg[ExchangeEndpoint.MSG_STRUCT_TYPE],
                                                                           msg[ExchangeEndpoint.MSG_STRUCT_SUBTYPE]))
                    continue
                self.MqttClient.publish(topic, msg[ExchangeEndpoint.MSG_STRUCT_DATA])

        # Check for any MQTT messages, the callback is called when a message
        # has arrived. If no message is pending this function check_msg will return.
        self.MqttClient.check_msg()

    @staticmethod
    def InstanceGet():
        return DataExchange._Instance


class Endpoint:

    def __init__(self):
        self.DataEx = DataExchange.InstanceGet()

    def MessagePut(self, msg_data_dict, msg_type, msg_subtype):
        self.DataEx.MessagePut(msg_data_dict, msg_type, msg_subtype)

    def MessageGet(self, msg_type, msg_subtype):
        return self.DataEx.MessageGet(msg_type, msg_subtype)

