import uasyncio
import umqtt.simple

import utime
import uerrno
import ustruct

from micropython import const

from middleware.Singleton import Singleton
from Message import Message


class DataSink():
    def __init__(self, max_count):
        self.MaxCount = max_count
        self.ReadIndex = 0
        
    def Get(self, msg_type, msg_subtype):
        return ExchangeEndpoint.SinkMessageGet(msg_type, msg_subtype)


class DataSource():
    def __init__(self, max_count):
        self.MaxCount = max_count
    
    def Put(self, msg_data_dict, msg_type, msg_subtype):
        if ExchangeEndpoint.SourceMessageCount() >= self.MaxCount:
            return uerrno.ENOSPC
        ExchangeEndpoint.SourceMessagePut(msg_data_dict, msg_type, msg_subtype)
        return 0

class DataExchange(object):
    
    CONNECT_RETRY_INTERVAL_SEC  = const(5)
    MSG_URL_LEN_MAX             = const(30)
    
    MSG_MAP_TYPE    = const(0)
    MSG_MAP_SUBTYPE = const(1)
    MSG_MAP_URL     = const(2)

    _SingletonInstance = Singleton.Singleton()
    ExchangeBuffer = bytearray(ExchangeEndpoint.MSG_DATA_LEN_MAX)

    def __init__(self, directory, mqtt_client_obj, client_id, mqtt_retries):

        self.Sources = set()
        self.Sinks = set()
        self.MessageMapping = set()
        self.MqttClient = mqtt_client_obj
        self.MqttRetries = mqtt_retries
        
        Message.DeviceId(client_id)
        ExchangeEndpoint.FileDir(directory)
        
    def RegisterDataSource(self, source):
        self.Sources.add(source)
        
    def RegisterDataSink(self, sink):
        self.Sinks.add(sink)
    
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

def Service():
    data_ex = DataExchange.InstanceGet()

    data_ex.MqttSetup()
    if ExchangeEndpoint.SourceMessageCount() > 0:
        for msg in ExchangeEndpoint.SourceMessageFile:
            topic = data_ex.UrlFromMessageType(msg[ExchangeEndpoint.MSG_STRUCT_TYPE],
                                       msg[ExchangeEndpoint.MSG_STRUCT_SUBTYPE])
            if topic is None:
                print("Warning: No topic defined for message %d.%d" % (msg[ExchangeEndpoint.MSG_STRUCT_TYPE],
                                                                       msg[ExchangeEndpoint.MSG_STRUCT_SUBTYPE]))
                continue
            DataExchange.MqttClient.publish(topic, msg[ExchangeEndpoint.MSG_STRUCT_DATA])

    # Check for any MQTT messages, the callback is called when a message
    # has arrived. If no message is pending this function check_msg will return.
    DataExchange.MqttClient.check_msg()
