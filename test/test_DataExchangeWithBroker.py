import sys
sys.path.append('../src/')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from module.DataExchange.DataExchange import DataExchange
from module.DataExchange.DataExchange import Endpoint

# Other
from module.DataExchange.Message import Message
from module.SystemTime import SystemTime
from umqtt.simple import MQTTClient
import utime


class test_DataExchangeWithBroker(unittest.TestCase):

    DIR = "./"
    ID = '123'
    RETRIES = 3
    BROKER = '192.168.0.103'
    PORT = 1883

    MqttClient = None
    DataEx = None
    Time = SystemTime.InstanceAcquire()
    RecvTopic = None
    RecvMsg = None
    RecvMsgCount = 0

    SystemTime.Service()

    def setUp(arg):
        test_DataExchangeWithBroker.RecvMsgCount = 0
        test_DataExchangeWithBroker.RecvTopic = None
        test_DataExchangeWithBroker.RecvMsg = None
        test_DataExchangeWithBroker.MqttClient = MQTTClient(test_DataExchangeWithBroker.ID,
                                                            test_DataExchangeWithBroker.BROKER,
                                                            test_DataExchangeWithBroker.PORT)
        test_DataExchangeWithBroker.DataEx = DataExchange(test_DataExchangeWithBroker.DIR,
                                                          test_DataExchangeWithBroker.MqttClient,
                                                          test_DataExchangeWithBroker.ID,
                                                          test_DataExchangeWithBroker.RETRIES)

    def tearDown(arg):
        test_DataExchangeWithBroker.DataEx.Reset()

    @staticmethod
    def MqttMsgRecvCallback(topic, msg):
        test_DataExchangeWithBroker.RecvTopic = topic
        test_DataExchangeWithBroker.RecvMsg = msg
        test_DataExchangeWithBroker.RecvMsgCount = test_DataExchangeWithBroker.RecvMsgCount + 1

    def test_MqttClient(self):
        self.MqttClient.set_callback(test_DataExchangeWithBroker.MqttMsgRecvCallback)

        connected = False
        while connected is False:
            try:
                print(self.MqttClient.connect())
                connected = True
                print("[MQTT] Connected.")
            except OSError:
                utime.sleep(2)
                continue

        self.assertTrue(connected)

    def test_PublishReceiveMessageRoundTrip(self):
        ep = Endpoint()

        msg_type = 3
        msg_subtype = 3
        msg_url = "<pn>/<id>/temp"
        msg = {"test": "msg"}
        msg_dir = DataExchange.MSG_DIRECTION_BOTH

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)

        # Initialize the Service on the first run
        self.DataEx.Service()

        ep.MessagePut(msg, msg_type, msg_subtype)

        # Run the Service again to publish the message.
        self.DataEx.Service()

        utime.sleep(1)

        # Run the Service again to receive the message.
        self.DataEx.Service()

        recv_msg = ep.MessageGet(msg_type, msg_subtype)
        print(recv_msg)
        self.assertEqual(recv_msg[Message.MSG_SECTION_DATA], msg)

