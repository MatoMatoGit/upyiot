import uasyncio
import uasyncio.queues
import umqtt.simple
import ujson
from micropython import const

class ExchangeEndPoint(object):
    
    def __init__(self, mtype, msub_type, url):
        self.Queue = uasyncio.Queue()
        self.Type = mtype
        self.SubType = msub_type
        self.Url = url

    def Queue(self):
        return self.Queue
    
    def PutNoWait(self, *args):
        if self.Queue.full() is True:
            return -1

        return 0
    
    def Get(self):
        self.Queue.get()
        
    
class Sink(ExchangeEndPoint):
    
    def __init__(self, mtype, msub_type, url):
        super.__init__(mtype, msub_type, url)   


class Source(ExchangeEndPoint):
    
    def __init__(self, mtype, msub_type, url, schema):
        super.__init__(mtype, msub_type, url)
        self.Schema = schema

class DataExchange(object):
    
    DATA_EXCHANGE_INTERVAL_SEC = const(10)
    CONNECT_RETRY_INTERVAL_SEC = const(5)
    
    def __init__(self, mqtt_client_obj, time_obj):
        self.Time = time_obj
        self.Sources = set()
        self.Sinks = set()
        self.MqttClient = mqtt_client_obj
        
        
    def RegisterDataSource(self, source):
        self.Sources.add(source)
        
    def RegisterDataSink(self, sink):
        self.Sinks.add(sink)
    
    @staticmethod
    async def Service():
        DataExchange.__MqttSetup()
        
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
            
            await uasyncio.sleep(DataExchange.DATA_EXCHANGE_INTERVAL_SEC)
    
    @staticmethod
    def __MqttSetup():
        print("[MQTT] Connecting to server.")
        connected = False
        # Try to connect the MQTT server, if it fails rety after the specified
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
        
        
    
        