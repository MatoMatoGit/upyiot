import sys
sys.path.append('../src/')

# Test libraries
import unittest
from TestUtil import TestUtil
from stubs import DummySensor

# Unit Under Test
from module.DataExchange.DataExchange import DataExchange
from module.DataExchange.DataExchange import Endpoint
from module.DataExchange.MessageFormatAdapter import MessageFormatAdapter
from middleware.Sensor import Sensor

# Other
from module.DataExchange.Message import Message
from module.SystemTime import SystemTime
from umqtt.simple import MQTTClient
import utime


class test_SensorToBroker(unittest.TestCase):

    DIR = "./"
    ID = '3f7e12c9'
    RETRIES = 3
    BROKER = '192.168.0.103'
    PORT = 1883

    MqttClient = None
    DataEx = None
    Time = SystemTime.InstanceAcquire()
    RecvTopic = None
    RecvMsg = None
    RecvMsgCount = 0

    SensorName = "dummy"
    Sensor = None
    Samples = [20, 21, 25, 30, 35, 35, 20, 12, 10, 40]

    SystemTime.Service()

    def setUp(arg):
        filter_depth = len(test_SensorToBroker.Samples)
        dummy = DummySensor.DummySensor(test_SensorToBroker.Samples)
        test_SensorToBroker.Sensor = Sensor.Sensor(test_SensorToBroker.DIR,
                                                   test_SensorToBroker.SensorName,
                                                   filter_depth, dummy)
        test_SensorToBroker.MqttClient = MQTTClient(test_SensorToBroker.ID,
                                                    test_SensorToBroker.BROKER,
                                                    test_SensorToBroker.PORT)
        test_SensorToBroker.DataEx = DataExchange(test_SensorToBroker.DIR,
                                                  test_SensorToBroker.MqttClient,
                                                  test_SensorToBroker.ID,
                                                  test_SensorToBroker.RETRIES)
        test_SensorToBroker.RecvMsgCount = 0
        test_SensorToBroker.RecvTopic = None
        test_SensorToBroker.RecvMsg = None

    def tearDown(arg):
        test_SensorToBroker.DataEx.Reset()

    @staticmethod
    def MqttMsgRecvCallback(topic, msg):
        test_SensorToBroker.RecvTopic = topic
        test_SensorToBroker.RecvMsg = msg
        test_SensorToBroker.RecvMsgCount = test_SensorToBroker.RecvMsgCount + 1

    def test_PublishSensorValues(self):

        # Message definition
        msg_type = 3
        msg_subtype = 1
        msg_url = "<pn>/<id>/temp"
        msg = {"arr": "", "n": 0}
        msg_dir = DataExchange.MSG_DIRECTION_BOTH

        # Create a Messaging Endpoint and a MessageFormatAdapter.
        ep = Endpoint()
        adapt = MessageFormatAdapter(ep, msg, msg_type, msg_subtype, MessageFormatAdapter.SEND_ON_COMPLETE)

        sample_stream = adapt.CreateStream("arr")
        sample_count_stream = adapt.CreateStream("n")

        # Register the temperature message type and topic.
        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)

        # Initialize the Messaging Service on the first run
        self.DataEx.Service()

        # Read sensor values.
        for i in range(0, 5):
            self.Sensor.Read()

        # Get the store sensor values and write them
        # to the sample stream.
        sample_count_stream.write(self.Sensor.SamplesCount)
        buf = [None] * self.Sensor.SamplesCount
        self.Sensor.SamplesGet(buf)
        sample_stream.write(buf)

        utime.sleep(5)

        # Sync time
        SystemTime.Service()

        # Read sensor values.
        for i in range(0, 5):
            self.Sensor.Read()

        # Get the store sensor values and write them
        # to the sample stream.
        sample_count_stream.write(self.Sensor.SamplesCount)
        buf = [None] * self.Sensor.SamplesCount
        self.Sensor.SamplesGet(buf)
        sample_stream.write(buf)

        # Run the Service again to publish the messages.
        self.DataEx.Service()

        utime.sleep(1)

        # Run the Service again to receive the message.
        self.DataEx.Service()

        # Receive both published temperature messages.
        recv_msg = ep.MessageGet(msg_type, msg_subtype)
        print("Received message: {}".format(recv_msg))
        recv_msg = ep.MessageGet(msg_type, msg_subtype)
        print("Received message: {}".format(recv_msg))

