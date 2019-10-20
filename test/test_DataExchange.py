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
from module.SystemTime import SystemTime

from umqtt.simple import MQTTClient as UMqttClient

class test_DataExchange(unittest.TestCase):

    DIR = "./"
    ID = "32"
    RETRIES = 3

    MqttClient = None
    DataEx = None
    Time = SystemTime.InstanceAcquire()
    RecvTopic = None
    RecvMsg = None
    RecvMsgCount = 0

    SystemTime.Service()

    def setUp(arg):
        test_DataExchange.RecvMsgCount = 0
        test_DataExchange.RecvTopic = None
        test_DataExchange.RecvMsg = None
        test_DataExchange.MqttClient = MQTTClient()
        test_DataExchange.DataEx = DataExchange(test_DataExchange.DIR, test_DataExchange.MqttClient,
                                                test_DataExchange.ID, test_DataExchange.RETRIES)

    def tearDown(arg):
        test_DataExchange.DataEx.Reset()
        return

    def test_Constructor(self):
        self.assertIsNotNone(self.DataEx.SendMessageBuffer)
        self.assertEqual(Message.DeviceId(), test_DataExchange.ID)
        self.assertTrue(self.DataEx.SendMessageBuffer.IsConfigured())

    @staticmethod
    def MqttMsgRecvCallback(topic, msg):
        test_DataExchange.RecvTopic = topic
        test_DataExchange.RecvMsg = msg
        test_DataExchange.RecvMsgCount = test_DataExchange.RecvMsgCount + 1

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

    def test_RegisterMessageTypeWithIdField(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "<id>/sensor/temp"
        exp_msg_url = test_DataExchange.ID + "/sensor/temp"
        msg_dir = DataExchange.MSG_DIRECTION_RECV

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        msg_map = self.DataEx.MessageMapFromType(msg_type, msg_subtype)

        self.assertEqual(msg_map[DataExchange.MSG_MAP_URL], exp_msg_url)

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
        self.assertEqual(msg_tuple[MessageBuffer.MSG_STRUCT_TYPE], msg_type)
        self.assertEqual(msg_tuple[MessageBuffer.MSG_STRUCT_SUBTYPE], msg_subtype)
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

        Message.Serialize("2019-09-04T23:34:44", msg, msg_type, msg_subtype)
        buf.MessagePut(Message.Stream().getvalue().decode('utf-8'))
        recv_msg = self.DataEx.MessageGet(msg_type, msg_subtype)
        print(recv_msg)
        print(type(recv_msg))
        self.assertEqual(recv_msg[Message.MSG_SECTION_DATA], msg)

    def test_MessageGetNoMessageReceived(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_dir = DataExchange.MSG_DIRECTION_BOTH

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        recv_msg = self.DataEx.MessageGet(msg_type, msg_subtype)

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

    def test_ServicePublishMessage(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg = {"test": "msg"}
        msg_dir = DataExchange.MSG_DIRECTION_SEND

        # Initialize the Service on the first run
        self.DataEx.Service()

        # Override the MQTT message receive callback set by the Service
        # so messages are received by the test.
        self.MqttClient.set_callback(test_DataExchange.MqttMsgRecvCallback)
        # Subscribe to the topic.
        self.MqttClient.subscribe(msg_url)

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        self.DataEx.MessagePut(msg, msg_type, msg_subtype)

        # Run the Service again to publish the message
        self.DataEx.Service()

        recv_msg = Message.Deserialize(self.RecvMsg)
        self.assertEqual(self.RecvMsgCount, 1)
        print(recv_msg)
        self.assertEqual(recv_msg[Message.MSG_SECTION_DATA], msg)

    def test_ServicePublishAndReceiveRoundTrip(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg = {"test": "msg"}
        msg_dir = DataExchange.MSG_DIRECTION_BOTH

        # Initialize the Service on the first run
        self.DataEx.Service()

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        self.DataEx.MessagePut(msg, msg_type, msg_subtype)

        # Run the Service again to publish and check for received messages.
        self.DataEx.Service()

        recv_msg = self.DataEx.MessageGet(msg_type, msg_subtype)
        print(recv_msg)
        self.assertEqual(recv_msg[Message.MSG_SECTION_DATA], msg)


class test_Endpoint(unittest.TestCase):

    DIR = "./"
    ID = "32"
    RETRIES = 3

    MqttClient = None
    DataEx = None
    Ep = None

    def setUp(arg):
        test_Endpoint.MqttClient = MQTTClient()
        test_Endpoint.DataEx = DataExchange(test_Endpoint.DIR, test_Endpoint.MqttClient,
                                            test_Endpoint.ID, test_Endpoint.RETRIES)
        test_Endpoint.Ep = Endpoint()

    def tearDown(arg):
        test_Endpoint.DataEx.Reset()
        return

    def test_Constructor(self):
        self.assertEqual(self.Ep.DataEx, self.DataEx)

    def test_MultipleInstances(self):
        ep = Endpoint()
        self.assertEqual(self.Ep.DataEx, self.DataEx)
        self.assertEqual(ep.DataEx, self.DataEx)

    def test_MessagePut(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg = {"test": "msg"}
        msg_dir = DataExchange.MSG_DIRECTION_BOTH

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        res = self.Ep.MessagePut(msg, msg_type, msg_subtype)

        self.assertEqual(res, 1)

    def test_MessageGet(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg = {"test": "msg"}
        msg_dir = DataExchange.MSG_DIRECTION_BOTH

        self.DataEx.RegisterMessageType(msg_type, msg_subtype, msg_url, msg_dir)
        msg_map = self.DataEx.MessageMapFromType(msg_type, msg_subtype)
        buf = msg_map[DataExchange.MSG_MAP_RECV_BUFFER]

        Message.Serialize("2019-09-04T23:34:44", msg, msg_type, msg_subtype)
        buf.MessagePut(Message.Stream().getvalue().decode('utf-8'))
        recv_msg = self.Ep.MessageGet(msg_type, msg_subtype)
        self.assertEqual(recv_msg[Message.MSG_SECTION_DATA], msg)
