import sys
sys.path.append('../src/')

# Test libraries
import unittest
from TestUtil import TestUtil
from stubs.MqttClientStub import MQTTClient

# Unit Under Test
from module.DataExchange.DataExchange import DataExchange
from module.DataExchange.DataExchange import Endpoint

# Other
from module.DataExchange.Message import Message
from module.DataExchange.MessageBuffer import MessageBuffer


class test_DataExchange(unittest.TestCase):

    DIR = "./"
    ID = 32
    RETRIES = 3

    MqttClient = None
    DataEx = None

    def setUp(arg):
        test_DataExchange.MqttClient = MQTTClient()
        test_DataExchange.DataEx = DataExchange(test_DataExchange.DIR, test_DataExchange.MqttClient,
                                                test_DataExchange.ID, test_DataExchange.RETRIES)

    def tearDown(arg):
        return

    def test_Constructor(self):
        self.assertIsNotNone(self.DataEx.SendMessageBuffer)
        self.assertEqual(Message.DeviceId(), test_DataExchange.ID)
        self.assertTrue(self.DataEx.SendMessageBuffer.IsConfigured())

    def test_RegisterMessageTypeDirectionSend(self):
        msg_type = 1
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_dir = DataExchange.MSG_DIRECTION_SEND

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        msg_map = self.DataEx.MessageMapFromType(msg_type, msg_subtype)
        print(msg_map)
        self.assertEqual(msg_map[DataExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[DataExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[DataExchange.MSG_MAP_URL], msg_url)
        self.assertIsNone(msg_map[DataExchange.MSG_MAP_RECV_BUFFER])

    def test_RegisterMessageTypeDirectionReceive(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_dir = DataExchange.MSG_DIRECTION_RECV

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        msg_map = self.DataEx.MessageMapFromType(msg_type, msg_subtype)

        self.assertEqual(msg_map[DataExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[DataExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[DataExchange.MSG_MAP_URL], msg_url)
        self.assertIsNotNone(msg_map[DataExchange.MSG_MAP_RECV_BUFFER])
        self.assertIsInstance(msg_map[DataExchange.MSG_MAP_RECV_BUFFER], MessageBuffer)


class test_Endpoint(unittest.TestCase):

    DIR = "./"
    ID = ""
    RETRIES = 3

    MqttClient = None
    DataEx = None

    def setUp(arg):
        test_DataExchange.MqttClient = MQTTClient()
        test_DataExchange.DataEx = DataExchange(test_DataExchange.DIR, test_DataExchange.MqttClient,
                                                test_DataExchange.ID, test_DataExchange.RETRIES)

    def tearDown(arg):
        return

    def test_Constructor(self):

        return

