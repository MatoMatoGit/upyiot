import sys
sys.path.append('../upyiot/')

# Test libraries
import unittest
from TestUtil import TestUtil
from stubs import DummySensor
from ExampleMessage import ExampleMessage

# Unit Under Test
from module.Messaging.MessageExchange import MessageExchange
from module.Messaging.MessageExchange import Endpoint
from module.Messaging.MessageFormatAdapter import MessageFormatAdapter
from module.Messaging.MessageSpecification import MessageSpecification
from middleware.Sensor import Sensor

# Other
from module.SystemTime.SystemTime import SystemTime
from umqtt.simple import MQTTClient
import utime


class test_SensorToBroker(unittest.TestCase):

    DIR = "./"
    ID = '3f7e12c9'
    RETRIES = 3
    BROKER = '192.168.0.103'
    PORT = 1883

    MqttClient = None
    MsgEx = None
    Time = SystemTime.InstanceGet()
    RecvTopic = None
    RecvMsg = None
    RecvMsgCount = 0
    UrlFields = {MessageSpecification.URL_FIELD_DEVICE_ID: ID,
                 MessageSpecification.URL_FIELD_PRODUCT_NAME: "smartsensor"}

    SensorName = "temp"
    Sensor = None
    Samples = [20, 21, 25, 30, 35, 35, 20, 12, 10, 40]

    Time.Service()

    def setUp(self):
        MessageSpecification.Config(self.UrlFields)
        filter_depth = len(self.Samples)
        dummy = DummySensor.DummySensor(self.Samples)
        self.Sensor = Sensor.Sensor(self.DIR,
                                    self.SensorName,
                                    filter_depth, dummy)
        self.MqttClient = MQTTClient(self.ID,
                                     self.BROKER,
                                     self.PORT)
        self.MsgEx = MessageExchange(self.DIR,
                                     self.MqttClient,
                                     self.ID,
                                     self.RETRIES)
        self.RecvMsgCount = 0
        self.RecvTopic = None
        self.RecvMsg = None

    def tearDown(self):
        self.MsgEx.Reset()
        self.Sensor.SamplesClear()

    @staticmethod
    def MqttMsgRecvCallback(topic, msg):
        test_SensorToBroker.RecvTopic = topic
        test_SensorToBroker.RecvMsg = msg
        test_SensorToBroker.RecvMsgCount = test_SensorToBroker.RecvMsgCount + 1

    def test_PublishSensorValues(self):

        # Message definition
        msg_spec = ExampleMessage()

        # Create a Messaging Endpoint and a MessageFormatAdapter.
        ep = Endpoint()
        adapt = MessageFormatAdapter(ep, MessageFormatAdapter.SEND_ON_COMPLETE, msg_spec)

        sample_stream = adapt.CreateStream(ExampleMessage.DATA_KEY_ARRAY)
        sample_count_stream = adapt.CreateStream(ExampleMessage.DATA_KEY_N)

        # Register the temperature message type and topic.
        self.MsgEx.RegisterMessageType(msg_spec)

        # Initialize the Messaging Service on the first run
        self.MsgEx.Service()

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
        self.Time.Service()

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
        self.MsgEx.Service()

        utime.sleep(1)

        # Run the Service again to receive the message.
        self.MsgEx.Service()

        # Receive both published temperature messages.
        recv_msg = ep.MessageGet(msg_spec.Type, msg_spec.Subtype)
        print("Received message: {}".format(recv_msg))
        recv_msg = ep.MessageGet(msg_spec.Type, msg_spec.Subtype)
        print("Received message: {}".format(recv_msg))

