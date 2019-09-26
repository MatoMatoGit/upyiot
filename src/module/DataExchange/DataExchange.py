import uasyncio
import umqtt.simple
import ujson
import utime
import uerrno
import ustruct
import uio
from micropython import const
from lib import StructFile
from builtins import None

class Message:
    
    SER_BUFFER_SIZE     = const(300)
    
    Msg = dict()
    MSG_SECTION_META     = "meta"
    MSG_SECTION_DATA     = "data"
    MSG_META_DATETIME    = "dt"
    MSG_META_VERSION     = "ver"
    MSG_META_TYPE        = "type"
    MSG_META_SUBTYPE     = "stype"
    MSG_META_ID          = "id"
    
    Msg[MSG_SECTION_META][MSG_META_DATETIME]   = "2019-09-04T23:34:44"
    Msg[MSG_SECTION_META][MSG_META_VERSION]    = 1
    Msg[MSG_SECTION_META][MSG_META_TYPE]       = 1
    Msg[MSG_SECTION_META][MSG_META_SUBTYPE]    = 1
    Msg[MSG_SECTION_META][MSG_META_ID]         = 0
        
    _SerBuffer = uio.BytesIO(SER_BUFFER_SIZE)
    
    @staticmethod
    def DeviceId(device_id=None):
        if device_id is None:
            return Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_ID]
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_ID] = device_id
    
    @staticmethod
    def Create(datetime, msg_data_dict, msg_type, msg_subtype):        
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_DATETIME] = datetime
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_TYPE] = msg_type
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_SUBTYPE] = msg_subtype
        Message.Msg[Message.MSG_SECTION_DATA] = msg_data_dict
    
    @staticmethod
    def Message():
        return Message.Msg
    
    @staticmethod
    def Serialize():
        ujson.dump(Message.Msg, Message._SerBuffer)
        return Message._SerBuffer

    @staticmethod
    def Deserialize():
        Message.Msg = ujson.load(Message._SerBuffer)
        return Message.Msg
        
class ExchangeEndpoint(object):
    
    MSG_DATA_LEN_MAX    = Message.SER_BUFFER_SIZE
    MSG_STRUCT_FMT      = "<II" + str(ExchangeEndpoint.MSG_DATA_LEN_MAX) + "s"
    MSG_STRUCT_TYPE     = const(0)
    MSG_STRUCT_SUBTYPE  = const(1)
    MSG_STRUCT_DATA     = const(2)
    
    SINK_MSG_FILE_ENTRY_TYPE    = const(0)
    SINK_MSG_FILE_ENTRY_SUBTYPE = const(1)
    SINK_MSG_FILE_ENTRY_FILE    = const(2)
    SING_MSG_FILE_ENTRY_READ_INDEX = const(3)
    
    Directory = ""
    SourceMessageFile = None
    SinkMessageFiles = []
    _PackBuffer = None
     
    @staticmethod
    def FileDir(directory):
        if ExchangeEndpoint.SourceMessageFile is None:
            ExchangeEndpoint.Directory = directory
            ExchangeEndpoint.SourceMessageFile = StructFile(directory + "/data_src",
                                                         ExchangeEndpoint.MSG_STRUCT_FMT)
        ExchangeEndpoint._PackBuffer = bytearray(ExchangeEndpoint.SourceMessageFile.DataSize + 
                                                 ExchangeEndpoint.MSG_DATA_LEN_MAX)


    @staticmethod
    def MessagePack(msg_type, msg_subtype, msg_data):
        ustruct.pack_into(ExchangeEndpoint.MSG_STRUCT_FMT, ExchangeEndpoint._PackBuffer, 0,
                          msg_type, msg_subtype, msg_data)
        return ExchangeEndpoint._PackBuffer
    
    @staticmethod
    def SourceMessagePut(msg_data_dict, msg_type, msg_subtype):
        Message.Create(utime.datetime(), msg_data_dict, msg_type, msg_subtype)
        ExchangeEndpoint.SourceMessageFile.AppendStruct(
            ExchangeEndpoint.MessagePack(msg_type, msg_subtype, 
                                         Message.Serialize()))

    @staticmethod
    def SourceMessageCount():
        return ExchangeEndpoint.SourceMessageFile.Count
    
    @staticmethod
    def SinkMessageFileInit(msg_type, msg_subtype):
        struct_file = StructFile(ExchangeEndpoint.Directory + "/data_snk_" + str(msg_type) 
                           + "_" + str(msg_subtype), ExchangeEndpoint.MSG_STRUCT_FMT)
        sink_msg_entry = [msg_type, msg_subtype, struct_file, 0]
        ExchangeEndpoint.SinkMessageFiles.append(sink_msg_entry)
        
    @staticmethod
    def _SinkMessageEntryIndexGet(msg_type, msg_subtype):
        i = 0
        for sink_msg_entry in ExchangeEndpoint.SinkMessageFiles:
            if sink_msg_entry[ExchangeEndpoint.SINK_MSG_FILE_ENTRY_TYPE] is msg_type and \
            sink_msg_entry[ExchangeEndpoint.SINK_MSG_FILE_ENTRY_SUBTYPE] is msg_subtype:
                return i
            i = i + 1
        return None
    
    @staticmethod
    def SinkMessageGet(msg_type, msg_subtype):
        entry_index = ExchangeEndpoint._SinkMessageEntryIndexGet(msg_type, msg_subtype)
        file = ExchangeEndpoint.SinkMessageFiles[entry_index][ExchangeEndpoint.SINK_MSG_FILE_ENTRY_FILE]
        read_index = ExchangeEndpoint.SinkMessageFiles[entry_index][ExchangeEndpoint.SING_MSG_FILE_ENTRY_READ_INDEX]
        
        if read_index >= file.Count:
            return None
        
        
        ExchangeEndpoint.SinkMessageFiles[entry_index][ExchangeEndpoint.SING_MSG_FILE_ENTRY_READ_INDEX] = read_index + 1   
        

class DataSink():
    def __init__(self, max_count):
        self.MaxCount = max_count
        self.ReadIndex = 0
        
    def Get(self, msg_type, msg_subtype):
        return SinkMessageGet(msg_type, msg_subtype)


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
    
    def __init__(self, directory, mqtt_client_obj, client_id):
        self.Sources = set()
        self.Sinks = set()
        self.MessageMapping = set()
        self.MqttClient = mqtt_client_obj
        
        Message.DeviceId(client_id)
        ExchangeEndpoint.FileDir(directory)
        
    def RegisterDataSource(self, source):
        self.Sources.add(source)
        
    def RegisterDataSink(self, sink):
        self.Sinks.add(sink)
    
    def RegisterMessageMapping(self, msg_type, msg_subtype, url):
        self.MessageMapping.add((msg_type, msg_subtype, url))
        
    
    def _UrlFromMessageType(self, msg_type, msg_subtype):
        for msg in self.MessageTypes:
            if msg[DataExchange.MSG_MAP_TYPE] is msg_type \
            and msg[DataExchange.MSG_MAP_SUBTYPE] is msg_subtype:
                return msg[DataExchange.MSG_MAP_URL]
            return None

    @staticmethod
    def _MqttSetup():
        print("[MQTT] Connecting to server.")
        connected = False
        # Try to connect the MQTT server, if it fails retry after the specified
        # interval.
        while connected is False:
            try:
                DataExchange.MqttClient.connect()
                connected = True
                print("[MQTT] Connected.")
            except OSError:
                print("[MQTT] Failed to connect to server.")
                utime.sleep(DataExchange.CONNECT_RETRY_INTERVAL_SEC)
                continue
        # Set the MQTT callback which is called when a message arrives on a
        # topic.
        .0
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
    DataExchange._MqttSetup()
    # Check the registered sources for queued data.     
    for source in DataExchange.Sources:
        if source.
            data = source.get_nowait()
            # Convert the data to JSON and publish it.
            json_data = ujson.dump(data)
            DataExchange.MqttClient.publish(source.Url, json_data)
    
    # Check for any MQTT messages, the callback is called when a message
    # has arrived. If no message is pending this function check_msg will return.
    DataExchange.MqttClient.check_msg()
        

        