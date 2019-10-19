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

    def test_RegisterMessageTypeDirectionBoth(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_dir = DataExchange.MSG_DIRECTION_BOTH

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        msg_map = self.DataEx.MessageMapFromType(msg_type, msg_subtype)

        self.assertEqual(msg_map[DataExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[DataExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[DataExchange.MSG_MAP_URL], msg_url)
        self.assertIsNotNone(msg_map[DataExchange.MSG_MAP_RECV_BUFFER])
        self.assertIsInstance(msg_map[DataExchange.MSG_MAP_RECV_BUFFER], MessageBuffer)

    def test_MessageMapFromTypeEntryPresent(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_dir = DataExchange.MSG_DIRECTION_BOTH

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        msg_map = self.DataEx.MessageMapFromType(msg_type, msg_subtype)

        self.assertEqual(msg_map[DataExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[DataExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[DataExchange.MSG_MAP_URL], msg_url)

    def test_MessageMapFromTypeEntryNotPresent(self):
        msg_type = 3
        msg_subtype = 3

        msg_map = self.DataEx.MessageMapFromType(msg_type, msg_subtype)

        self.assertIsNone(msg_map)

    def test_MessageMapFromUrlEntryPresent(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_dir = DataExchange.MSG_DIRECTION_BOTH

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        msg_map = self.DataEx.MessageMapFromUrl(msg_url)

        self.assertEqual(msg_map[DataExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[DataExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[DataExchange.MSG_MAP_URL], msg_url)

    def test_MessageMapFromUrlEntryNotPresent(self):
        msg_url = "/sensor/temp"

        msg_map = self.DataEx.MessageMapFromUrl(msg_url)

        self.assertIsNone(msg_map)

    def test_MessagePut(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg = {"test": "msg"}
        msg_dir = DataExchange.MSG_DIRECTION_BOTH

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        res = self.DataEx.MessagePut(msg, msg_type, msg_subtype)
        msg_tuple = self.DataEx.SendMessageBuffer.MessageGet()

        self.assertEqual(res, 1)
        self.assertEqual(msg_tuple[MessageBuffer.MSG_STRUCT_TYPE], -1)
        self.assertEqual(msg_tuple[MessageBuffer.MSG_STRUCT_SUBTYPE], -1)
        self.assertEqual(Message.Deserialize(
            msg_tuple[MessageBuffer.MSG_STRUCT_DATA])[Message.MSG_SECTION_DATA], msg)

    def test_MessageGetSuccessful(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg = {"test": "msg"}
        msg_dir = DataExchange.MSG_DIRECTION_BOTH

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        msg_map = self.DataEx.MessageMapFromType(msg_type, msg_subtype)
        buf = msg_map[DataExchange.MSG_MAP_RECV_BUFFER]

        Message.Serialize(123, msg, msg_type, msg_subtype)
        buf.MessagePut(Message.Stream().getvalue().decode('utf-8'))
        recv_msg = self.DataEx.MessageGet(msg_type, msg_subtype)
        print(recv_msg)

        self.assertEqual(recv_msg[Message.MSG_SECTION_DATA], msg)

    def test_MessageGetNoMessageReceived(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_dir = DataExchange.MSG_DIRECTION_BOTH

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        recv_msg = self.DataEx.MessageGet(msg_type, msg_subtype)
        print(recv_msg)

        self.assertEqual(recv_msg, -3)

    def test_MessageGetTypeIsSend(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_dir = DataExchange.MSG_DIRECTION_SEND

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        recv_msg = self.DataEx.MessageGet(msg_type, msg_subtype)

        self.assertEqual(recv_msg, -2)

    def test_MessageGetTypeNotRegistered(self):
        msg_type = 3
        msg_subtype = 3

        recv_msg = self.DataEx.MessageGet(msg_type, msg_subtype)

        self.assertEqual(recv_msg, -1)

    def test_ServiceInitConnectSuccessfulNoRetries(self):

        self.DataEx.Service()

        connected = self.MqttClient.is_connected()
        callback_set = self.MqttClient.has_callback()

        self.assertTrue(connected)
        self.assertTrue(callback_set)

    def test_ServiceInitConnectSuccessfulAfterRetries(self):
        self.MqttClient.connect_fail_count(test_DataExchange.RETRIES - 1)
        self.DataEx.Service()

        connected = self.MqttClient.is_connected()
        callback_set = self.MqttClient.has_callback()

        self.assertTrue(connected)
        self.assertTrue(callback_set)

    def test_ServiceInitConnectFailureAfterRetries(self):
        self.MqttClient.connect_fail_count(test_DataExchange.RETRIES + 1)
        self.DataEx.Service()

        connected = self.MqttClient.is_connected()
        callback_set = self.MqttClient.has_callback()

        self.assertFalse(connected)
        self.assertTrue(callback_set)

    def test_ServiceInitSubscribe(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_dir = DataExchange.MSG_DIRECTION_BOTH

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        self.DataEx.Service()
        subscription = self.MqttClient.has_subscription(msg_url)

        self.assertTrue(subscription)







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

