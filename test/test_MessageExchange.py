import sys
sys.path.append('../')

# Test libraries
import unittest
from TestUtil import TestUtil
from stubs.MqttClientStub import MQTTClient

# Unit Under Test
from upyiot.comm.Messaging.MessageExchange import MessageExchange
from upyiot.comm.Messaging.MessageSpecification import MessageSpecification

# Other
from upyiot.comm.Messaging.Message import Message
from upyiot.comm.Messaging.MessageTemplate import *
from upyiot.comm.Messaging.Parser.JsonParser import JsonParser
from upyiot.comm.Messaging.MessageBuffer import MessageBuffer
from upyiot.comm.Messaging.Protocol.MqttProtocol import MqttProtocol
from upyiot.system.SystemTime.SystemTime import SystemTime
from upyiot.system.Service.Service import Service


class test_MessageExchange(unittest.TestCase):

    DIR = "./"
    ID = "32"
    RETRIES = 3
    MSG_SECTION_META = "meta"
    MSG_SECTION_DATA = "data"
    MSG_META_DATETIME = "dt"
    MSG_META_VERSION = "ver"
    MSG_META_TYPE = "type"
    MSG_META_SUBTYPE = "stype"
    MSG_META_ID = "id"

    MqttClient = None
    MsgEx = None
    Time = SystemTime.InstanceGet()
    RecvTopic = None
    RecvMsg = None
    RecvMsgCount = 0

    Metadata = {
        MSG_META_DATETIME:  "07-09-2020T20:00:00",
        MSG_META_VERSION:   1,
        MSG_META_TYPE:      1,
        MSG_META_SUBTYPE:   1,
        MSG_META_ID:        123,
    }

    Time.SvcRun()

    def setUp(arg):
        MessageTemplate.SectionsSet(test_MessageExchange.MSG_SECTION_META, test_MessageExchange.MSG_SECTION_DATA)
        MessageTemplate.MetadataTemplateSet(test_MessageExchange.Metadata)
        Message.SetParser(JsonParser())

        test_MessageExchange.RecvMsgCount = 0
        test_MessageExchange.RecvTopic = None
        test_MessageExchange.RecvMsg = None
        test_MessageExchange.MqttClient = MQTTClient()
        test_MessageExchange.MsgEx = MessageExchange(test_MessageExchange.DIR,
                                                     MqttProtocol(test_MessageExchange.MqttClient),
                                                     test_MessageExchange.RETRIES)

    def tearDown(arg):
        test_MessageExchange.MsgEx.Reset()
        return

    def test_Constructor(self):
        self.assertIsNotNone(self.MsgEx.SendMessageBuffer)
        self.assertTrue(self.MsgEx.SendMessageBuffer.IsConfigured())
        self.assertIsInstance(self.MsgEx, Service)

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
        msg_dir = MessageSpecification.MSG_DIRECTION_SEND

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromType(msg_type, msg_subtype)
        print(msg_map)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_ROUTING], msg_url)
        self.assertIsNone(msg_map[MessageExchange.MSG_MAP_RECV_BUFFER])

    def test_RegisterMessageTypeDirectionReceive(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg_dir = MessageSpecification.MSG_DIRECTION_RECV

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromType(msg_type, msg_subtype)

        self.assertEqual(msg_map[MessageExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_ROUTING], msg_url)
        self.assertIsNotNone(msg_map[MessageExchange.MSG_MAP_RECV_BUFFER])
        self.assertIsInstance(msg_map[MessageExchange.MSG_MAP_RECV_BUFFER], MessageBuffer)

    def test_RegisterMessageTypeDirectionBoth(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg_dir = MessageSpecification.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromType(msg_type, msg_subtype)

        self.assertEqual(msg_map[MessageExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_ROUTING], msg_url)
        self.assertIsNotNone(msg_map[MessageExchange.MSG_MAP_RECV_BUFFER])
        self.assertIsInstance(msg_map[MessageExchange.MSG_MAP_RECV_BUFFER], MessageBuffer)

    def test_MessageMapFromTypeEntryPresent(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg_dir = MessageSpecification.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromType(msg_type, msg_subtype)

        self.assertEqual(msg_map[MessageExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_ROUTING], msg_url)

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
        msg_dir = MessageSpecification.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromRoute(msg_url)

        self.assertEqual(msg_map[MessageExchange.MSG_MAP_TYPE], msg_type)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_SUBTYPE], msg_subtype)
        self.assertEqual(msg_map[MessageExchange.MSG_MAP_ROUTING], msg_url)

    def test_MessageMapFromUrlEntryNotPresent(self):
        msg_url = "/sensor/temp"

        msg_map = self.MsgEx.MessageMapFromRoute(msg_url)

        self.assertIsNone(msg_map)

    def test_MessagePut(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg = {"test": "msg"}
        msg_dir = MessageSpecification.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        res = self.MsgEx.MessagePut(msg, msg_type, msg_subtype)
        msg_tuple = self.MsgEx.SendMessageBuffer.MessageGet()

        self.assertEqual(res, 1)
        self.assertEqual(msg_tuple[MessageBuffer.MSG_STRUCT_TYPE], msg_type)
        self.assertEqual(msg_tuple[MessageBuffer.MSG_STRUCT_SUBTYPE], msg_subtype)
        self.assertEqual(Message.Deserialize(
            msg_tuple[MessageBuffer.MSG_STRUCT_DATA])[MessageTemplate.MSG_SECTION_DATA], msg)

    def test_MessageGetSuccessful(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg = {"test": "msg"}
        msg_dir = MessageSpecification.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        msg_map = self.MsgEx.MessageMapFromType(msg_type, msg_subtype)
        buf = msg_map[MessageExchange.MSG_MAP_RECV_BUFFER]

        Message.Serialize(msg)
        buf.MessagePut(Message.Stream().getvalue().decode('utf-8'))
        recv_msg = self.MsgEx.MessageGet(msg_type, msg_subtype)
        print(recv_msg)
        print(type(recv_msg))
        self.assertEqual(recv_msg[MessageTemplate.MSG_SECTION_DATA], msg)

    def test_MessageGetNoMessageReceived(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg_dir = MessageSpecification.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)
        recv_msg = self.MsgEx.MessageGet(msg_type, msg_subtype)

        self.assertEqual(recv_msg, -3)

    def test_MessageGetTypeIsSend(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg_data = {}
        msg_dir = MessageSpecification.MSG_DIRECTION_SEND

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

        self.MsgEx.SvcInit()

        connected = self.MqttClient.is_connected()
        callback_set = self.MqttClient.has_callback()

        self.assertTrue(connected)
        self.assertTrue(callback_set)

    def test_ServiceInitConnectSuccessfulAfterRetries(self):
        self.MqttClient.connect_fail_count(test_MessageExchange.RETRIES - 1)
        self.MsgEx.SvcInit()

        connected = self.MqttClient.is_connected()
        callback_set = self.MqttClient.has_callback()

        self.assertTrue(connected)
        self.assertTrue(callback_set)

    def test_ServiceInitConnectFailureAfterRetries(self):
        self.MqttClient.connect_fail_count(test_MessageExchange.RETRIES + 1)
        self.MsgEx.SvcInit()

        connected = self.MqttClient.is_connected()
        callback_set = self.MqttClient.has_callback()

        self.assertFalse(connected)
        self.assertTrue(callback_set)

    def test_ServiceSendMessage(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg = {"test": "msg"}
        msg_data  = {}
        msg_dir = MessageSpecification.MSG_DIRECTION_SEND

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        # Initialize the Service on the first run
        self.MsgEx.SvcInit()

        # Override the MQTT message receive callback set by the Service
        # so messages are received by the test.
        self.MqttClient.set_callback(test_MessageExchange.MqttMsgRecvCallback)
        # Subscribe to the topic.
        self.MqttClient.subscribe(msg_url)

        self.MsgEx.RegisterMessageType(msg_spec)
        self.MsgEx.MessagePut(msg, msg_type, msg_subtype)

        # Run the Service again to send the message
        self.MsgEx.SvcRun()

        recv_msg = Message.Deserialize(self.RecvMsg)
        self.assertEqual(self.RecvMsgCount, 1)
        print(recv_msg)
        self.assertEqual(recv_msg[MessageTemplate.MSG_SECTION_DATA], msg)

    def test_ServiceSendAndReceiveRoundTrip(self):
        msg_type = 3
        msg_subtype = 3
        msg_url = "/sensor/temp"
        msg = {"test": "msg"}
        msg_data = {}
        msg_dir = MessageSpecification.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg_data, msg_url, msg_dir)

        # Initialize the Service on the first run
        self.MsgEx.SvcInit()

        self.MsgEx.RegisterMessageType(msg_spec)
        self.MsgEx.MessagePut(msg, msg_type, msg_subtype)

        # Run the Service again to send and check for received messages.
        self.MsgEx.SvcRun()

        recv_msg = self.MsgEx.MessageGet(msg_type, msg_subtype)
        print(recv_msg)
        self.assertEqual(recv_msg[MessageTemplate.MSG_SECTION_DATA], msg)