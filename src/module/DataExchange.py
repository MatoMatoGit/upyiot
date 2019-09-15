import uasyncio
import umqtt.simple
import ujson
import utime
import uerrno
from micropython import const
from lib import StructFile
from zmq.backend import exc


class DataMessage:
    
    SER_BUFFER_SIZE     = const(300)
    
    Msg = dict()
    MSG_SECTION_META     = "meta"
    MSG_SECTION_DATA     = "data"
    MSG_META_DATETIME    = "dt"
    MSG_META_VERSION     = "ver"
    MSG_META_TYPE        = "type"
    MSG_META_SUBTYPE     = "sbtype"
    MSG_META_ID          = "id"
    
    Msg[MSG_SECTION_META][MSG_META_DATETIME]   = "2019-09-04T23:34:44"
    Msg[MSG_SECTION_META][MSG_META_VERSION]    = 1
    Msg[MSG_SECTION_META][MSG_META_TYPE]       = 1
    Msg[MSG_SECTION_META][MSG_META_SUBTYPE]    = 1
    Msg[MSG_SECTION_META][MSG_META_ID]         = 0
        
    _SerBuffer = bytearray(SER_BUFFER_SIZE)
    
    @staticmethod
    def DeviceId(device_id=None):
        if device_id is None:
            return DataMessage.Msg[DataMessage.MSG_SECTION_META][DataMessage.MSG_META_ID]
        DataMessage.Msg[DataMessage.MSG_SECTION_META][DataMessage.MSG_META_ID] = device_id
    
    @staticmethod
    def Create(datetime, msg_data_dict, msg_type, msg_subtype):
        if DataMessage._Instance is None:
            DataMessage.__init__(self)
        
        DataMessage.Msg[DataMessage.MSG_SECTION_META][DataMessage.MSG_META_DATETIME] = datetime
        DataMessage.Msg[DataMessage.MSG_SECTION_META][DataMessage.MSG_META_TYPE] = msg_type
        DataMessage.Msg[DataMessage.MSG_SECTION_META][DataMessage.MSG_META_SUBTYPE] = msg_subtype
        DataMessage.Msg[DataMessage.MSG_SECTION_DATA] = msg_data_dict
    
    @staticmethod
    def Message():
        return DataMessage.Msg
    
    @staticmethod
    def Serialize():
        ujson.dumpinto(DataMessage.Msg, DataMessage._SerBuffer)
        return DataMessage._SerBuffer

class ExchangeEndpoint(object):
    
    MSG_URL_LEN_MAX     = 30
    MSG_DATA_LEN_MAX    = DataMessage.SER_BUFFER_SIZE
    MSG_STRUCT_FMT      = "<ss"
    MSG_LEN_MAX         = MSG_URL_LEN_MAX + MSG_DATA_LEN_MAX
    
    SourceDataFile = None
    SinkDataFile = None
    _PackBuffer = bytearray(MSG_LEN_MAX)
    
    @staticmethod
    def FileDir(directory):
        if ExchangeEndpoint.SourceDataFile is None:
            ExchangeEndpoint.SourceDataFile = StructFile(directory + "/data_src", 
                                                         ExchangeEndpoint.MSG_STRUCT_FMT)
            ExchangeEndpoint.SinkDataFile = StructFile(directory + "/data_sink", 
                                                       ExchangeEndpoint.MSG_STRUCT_FMT)

    def __init__(self, max_count, mtype, msub_type, url):
        self.MaxCount = max_count
        self.Type = mtype
        self.SubType = msub_type
        self.MsgUrl = url
        self.MsgUrl.ljust(ExchangeEndpoint.MSG_URL_LEN_MAX, '\0')
        

class DataSink(ExchangeEndpoint):
    def __init__(self, max_count, mtype, msub_type, url):
        super().__init__(max_count, mtype, msub_type, url)
    
    def Put(self, json):
        if self.Queue.full() is True:
            return uerrno.ENODATA
        self.Queue.put(message)
        return 0
    
    def Get(self):
        """ Get a dictionary from the queue.
        """
        f = open('config.json', 'r')
        cfg = ujson.load(f)
        return self.Queue.get()
    
class DataSource(ExchangeEndpoint):
    def __init__(self, max_count, mtype, msub_type, url):
        super().__init__(max_count, mtype, msub_type, url)
    
    def Put(self, msg_data_dict, msg_type, msg_subtype):
        if ExchangeEndpoint.SourceDataFile.Count is self.MaxCount:
            return uerrno.ENODATA
        
        DataMessage.Create(utime.datetime(), msg_data_dict, msg_type, msg_subtype)
        ExchangeEndpoint.SourceDataFile.AppendData(self.MsgUrl, DataMessage.Serialize())
        
        return 0
    
    def Get(self):
        return self.Queue.get()

class DataExchange(object):
    
    CONNECT_RETRY_INTERVAL_SEC = const(5)
    
    def __init__(self, directory, mqtt_client_obj, client_id):
        self.Sources = set()
        self.Sinks = set()
        self.MqttClient = mqtt_client_obj
        DataMessage.DeviceId(client_id)
        ExchangeEndpoint.FileDir(directory)
        
    def RegisterDataSource(self, source):
        self.Sources.add(source)
        
    def RegisterDataSink(self, sink):
        self.Sinks.add(sink)
    
    @staticmethod
    async def Service(t_sleep_sec):
        DataExchange._MqttSetup()
        
        while True:      
            # Check the registered sources for queued data.     
            for source in DataExchange.Sources:
                while(source.empty() is False):
                    data = source.get_nowait()
                    # Convert the data to JSON and publish it.
                    json_data = ujson.dump(data)
                    DataExchange.MqttClient.publish(source.Url, json_data)
            
            # Check for any MQTT messages, the callback is called when a message
            # has arrived. If no message is pending this function check_msg will return.
            DataExchange.MqttClient.check_msg()
            
            await uasyncio.sleep(t_sleep_sec)
    
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
                uasyncio.sleep(DataExchange.CONNECT_RETRY_INTERVAL_SEC)
                continue
        # Set the MQTT callback which is called when a message arrives on a
        # topic.
        DataExchange.MqttClient.set_callback(DataExchange.__MqttCallback)
        
    
    def __MqttCallback(self, topic, msg):
        # Iterate through the registered sinks and check
        # if any of them has a URL matching the topic.
        for sink in DataExchange.Sinks:
            if sink.Url is topic:
                # Dump the JSON data to a dictionary and put
                # it in the sink's queue.
                data = ujson.dump(msg)
                sink.PutNoWait(data)
        
        
    
        