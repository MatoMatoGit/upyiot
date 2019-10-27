import sys
sys.path.append('../upyiot/')

# Test libraries
import unittest
from TestUtil import TestUtil
from stubs.MqttClientStub import MQTTClient

# Unit Under Test
from module.Messaging.MessageExchange import MessageExchange
from module.Messaging.MessageExchange import Endpoint
from module.Messaging.MessageSpecification import MessageSpecification

# Other
from module.Messaging.Message import Message
from module.Messaging.MessageBuffer import MessageBuffer
from module.SystemTime.SystemTime import SystemTime


class test_MessageExchange(unittest.TestCase):

    DIR = "./"
    ID = "32"
    RETRIES = 3

    MqttClient = None
    MsgEx = None
    Time = SystemTime.InstanceGet()
    RecvTopic = None
    RecvMsg = None
    RecvMsgCount = 0

    Time.Service()

    def setUp(arg):
        test_MessageExchange.RecvMsgCount = 0
        test_MessageExchange.RecvTopic = None
        test_MessageExchange.RecvMsg = None
        test_MessageExchange.MqttClient = MQTTClient()
        test_MessageExchange.MsgEx = MessageExchange(test_MessageExchange.DIR, test_MessageExchange.MqttClient,
                                                     test_MessageExchange.ID, test_MessageExchange.RETRIES)

    def tearDown(arg):
        test_MessageExchange.MsgEx.Reset()
        return

    def test_Constructor(self):
        self.assertIsNotNone(self.MsgEx.SendMessageBuffer)
        self.assertEqual(Message.DeviceId(), test_MessageExchange.ID)
        self.assertTrue(self.MsgEx.SendMessageBuffer.IsConfigured())

    @staticmethod
    def MqttMsgRecvCallback(topic, msg):
        test_MessageExchange.RecvTopic = topic
        test_MessageExchange.RecvMsg = msg
        test_MessageExchange.RecvMsgCount = test_MessageExchange.RecvMsgCount + 1

    def test_RegisterMessageTypeDirectionSend(self):
        msg_type = 1
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg_dir = MessageExchange.MSG_DIRECTION_SEND

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromType(msg_type, msg_subtype)
        print(msg_map)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_URL], msg_url)
        self.assertIsNone(msg_map[MessageExchange.MSG_MAP_RECV_BUFFER])

    def test_RegisterMessageTypeDirectionReceive(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg_dir = MessageExchange.MSG_DIRECTION_RECV

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromType(msg_type, msg_subtype)

        self.assertEqual(msg_map[MessageExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_URL], msg_url)
        self.assertIsNotNone(msg_map[MessageExchange.MSG_MAP_RECV_BUFFER])
        self.assertIsInstance(msg_map[MessageExchange.MSG_MAP_RECV_BUFFER], MessageBuffer)

    def test_RegisterMessageTypeWithIdField(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "<id>/sensor/temp"
        exp_msg_url = test_MessageExchange.ID + "/sensor/temp"
        msg_data = {}
        msg_dir = MessageExchange.MSG_DIRECTION_RECV

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromType(msg_type, msg_subtype)

        self.assertEqual(msg_map[MessageExchange.MSG_MAP_URL], exp_msg_url)

    def test_RegisterMessageTypeDirectionBoth(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg_dir = MessageExchange.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromType(msg_type, msg_subtype)

        self.assertEqual(msg_map[MessageExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_URL], msg_url)
        self.assertIsNotNone(msg_map[MessageExchange.MSG_MAP_RECV_BUFFER])
        self.assertIsInstance(msg_map[MessageExchange.MSG_MAP_RECV_BUFFER], MessageBuffer)

    def test_MessageMapFromTypeEntryPresent(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg_dir = MessageExchange.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromType(msg_type, msg_subtype)

        self.assertEqual(msg_map[MessageExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_URL], msg_url)

    def test_MessageMapFromTypeEntryNotPresent(self):
        msg_type = 3
        msg_subtype = 3

        msg_map = self.MsgEx.MessageMapFromType(msg_type, msg_subtype)

        self.assertIsNone(msg_map)

    def test_MessageMapFromUrlEntryPresent(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg_dir = MessageExchange.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromUrl(msg_url)

        self.assertEqual(msg_map[MessageExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_URL], msg_url)

    def test_MessageMapFromUrlEntryNotPresent(self):
        msg_url = "/sensor/temp"

        msg_map = self.MsgEx.MessageMapFromUrl(msg_url)

        self.assertIsNone(msg_map)

    def test_MessagePut(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg = {"test": "msg"}
        msg_dir = MessageExchange.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        res = self.MsgEx.MessagePut(msg, msg_type, msg_subtype)
        msg_tuple = self.MsgEx.SendMessageBuffer.MessageGet()

        self.assertEqual(res, 1)
        self.assertEqual(msg_tuple[MessageBuffer.MSG_STRUCT_TYPE], msg_type)
        self.assertEqual(msg_tuple[MessageBuffer.MSG_STRUCT_SUBTYPE], msg_subtype)
        self.assertEqual(Message.Deserialize(
            msg_tuple[MessageBuffer.MSG_STRUCT_DATA])[Message.MSG_SECTION_DATA], msg)

    def test_MessageGetSuccessful(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg = {"test": "msg"}
        msg_dir = MessageExchange.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromType(msg_type, msg_subtype)
        buf = msg_map[MessageExchange.MSG_MAP_RECV_BUFFER]

        Message.Serialize("2019-09-04T23:34:44", msg, msg_type, msg_subtype)
        buf.MessagePut(Message.Stream().getvalue().decode('utf-8'))
        recv_msg = self.MsgEx.MessageGet(msg_type, msg_subtype)
        print(recv_msg)
        print(type(recv_msg))
        self.assertEqual(recv_msg[Message.MSG_SECTION_DATA], msg)

    def test_MessageGetNoMessageReceived(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg_dir = MessageExchange.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        recv_msg = self.MsgEx.MessageGet(msg_type, msg_subtype)

        self.assertEqual(recv_msg, -3)

    def test_MessageGetTypeIsSend(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg_dir = MessageExchange.MSG_DIRECTION_SEND

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        recv_msg = self.MsgEx.MessageGet(msg_type, msg_subtype)

        self.assertEqual(recv_msg, -2)

    def test_MessageGetTypeNotRegistered(self):
        msg_type = 3
        msg_subtype = 3

        recv_msg = self.MsgEx.MessageGet(msg_type, msg_subtype)

        self.assertEqual(recv_msg, -1)

    def test_ServiceInitConnectSuccessfulNoRetries(self):

        self.MsgEx.Service()

        connected = self.MqttClient.is_connected()
        callback_set = self.MqttClient.has_callback()

        self.assertTrue(connected)
        self.assertTrue(callback_set)

    def test_ServiceInitConnectSuccessfulAfterRetries(self):
        self.MqttClient.connect_fail_count(test_MessageExchange.RETRIES - 1)
        self.MsgEx.Service()

        connected = self.MqttClient.is_connected()
        callback_set = self.MqttClient.has_callback()

        self.assertTrue(connected)
        self.assertTrue(callback_set)

    def test_ServiceInitConnectFailureAfterRetries(self):
        self.MqttClient.connect_fail_count(test_MessageExchange.RETRIES + 1)
        self.MsgEx.Service()

        connected = self.MqttClient.is_connected()
        callback_set = self.MqttClient.has_callback()

        self.assertFalse(connected)
        self.assertTrue(callback_set)

    def test_ServiceInitSubscribe(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg_dir = MessageExchange.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        self.MsgEx.Service()
        subscription = self.MqttClient.has_subscription(msg_url)

        self.assertTrue(subscription)

    def test_ServicePublishMessage(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg = {"test": "msg"}
        msg_data  = {}
        msg_dir = MessageExchange.MSG_DIRECTION_SEND

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        # Initialize the Service on the first run
        self.MsgEx.Service()

        # Override the MQTT message receive callback set by the Service
        # so messages are received by the test.
        self.MqttClient.set_callback(test_MessageExchange.MqttMsgRecvCallback)
        # Subscribe to the topic.
        self.MqttClient.subscribe(msg_url)

        self.MsgEx.RegisterMessageType(msg_spec)
        self.MsgEx.MessagePut(msg, msg_type, msg_subtype)

        # Run the Service again to publish the message
        self.MsgEx.Service()

        recv_msg = Message.Deserialize(self.RecvMsg)
        self.assertEqual(self.RecvMsgCount, 1)
        print(recv_msg)
        self.assertEqual(recv_msg[Message.MSG_SECTION_DATA], msg)

    def test_ServicePublishAndReceiveRoundTrip(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg = {"test": "msg"}
        msg_data = {}
        msg_dir = MessageExchange.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        # Initialize the Service on the first run
        self.MsgEx.Service()

        self.MsgEx.RegisterMessageType(msg_spec)
        self.MsgEx.MessagePut(msg, msg_type, msg_subtype)

        # Run the Service again to publish and check for received messages.
        self.MsgEx.Service()

        recv_msg = self.MsgEx.MessageGet(msg_type, msg_subtype)
        print(recv_msg)
        self.assertEqual(recv_msg[Message.MSG_SECTION_DATA], msg)


class test_Endpoint(unittest.TestCase):

    DIR = "./"
    ID = "32"
    RETRIES = 3

    MqttClient = None
    MsgEx = None
    Ep = None

    def setUp(arg):
        test_Endpoint.MqttClient = MQTTClient()
        test_Endpoint.MsgEx = MessageExchange(test_Endpoint.DIR, test_Endpoint.MqttClient,
                                              test_Endpoint.ID, test_Endpoint.RETRIES)
        test_Endpoint.Ep = Endpoint()

    def tearDown(arg):
        test_Endpoint.MsgEx.Reset()
        return

    def test_Constructor(self):
        self.assertEqual(self.Ep.MsgEx, self.MsgEx)

    def test_MultipleInstances(self):
        ep = Endpoint()
        self.assertEqual(self.Ep.MsgEx, self.MsgEx)
        self.assertEqual(ep.MsgEx, self.MsgEx)

    def test_MessagePut(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg = {"test": "msg"}
        msg_data = {}
        msg_dir = MessageExchange.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        res = self.Ep.MessagePut(msg, msg_type, msg_subtype)

        self.assertEqual(res, 1)

    def test_MessageGet(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg = {"test": "msg"}
        msg_data ={}
        msg_dir = MessageExchange.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromType(msg_type, msg_subtype)
        buf = msg_map[MessageExchange.MSG_MAP_RECV_BUFFER]

        Message.Serialize("2019-09-04T23:34:44", msg, msg_type, msg_subtype)
        buf.MessagePut(Message.Stream().getvalue().decode('utf-8'))
        recv_msg = self.Ep.MessageGet(msg_type, msg_subtype)
        self.assertEqual(recv_msg[Message.MSG_SECTION_DATA], msg)
