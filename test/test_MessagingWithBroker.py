import sys
sys.path.append('../')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from upyiot.module.Messaging.MessageExchange import MessageExchange
from upyiot.module.Messaging.MessageExchange import Endpoint
from upyiot.module.Messaging.MessageSpecification import MessageSpecification

# Other
from upyiot.module.Messaging.Message import Message
from upyiot.module.SystemTime.SystemTime import SystemTime
from umqtt.simple import MQTTClient
import utime


class test_MessagingWithBroker(unittest.TestCase):

    DIR = "./"
    ID = '123'
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

    Time.SvcRun()

    def setUp(self):
        MessageSpecification.Config(self.UrlFields)
        self.RecvMsgCount = 0
        self.RecvTopic = None
        self.RecvMsg = None
        self.MqttClient = MQTTClient(self.ID,
                                     self.BROKER,
                                     self.PORT)
        self.MsgEx = MessageExchange(self.DIR,
                                     self.MqttClient,
                                     self.ID,
                                     self.RETRIES)

    def tearDown(self):
        self.MsgEx.Reset()

    @staticmethod
    def MqttMsgRecvCallback(topic, msg):
        test_MessagingWithBroker.RecvTopic = topic
        test_MessagingWithBroker.RecvMsg = msg
        test_MessagingWithBroker.RecvMsgCount = test_MessagingWithBroker.RecvMsgCount + 1

    def test_MqttClient(self):
        self.MqttClient.set_callback(test_MessagingWithBroker.MqttMsgRecvCallback)

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

    def test_PutGetMessageRoundTrip(self):
        ep = Endpoint()

        msg_type = 3
        msg_subtype = 3
        msg_url = "<pn>/<id>/temp"
        msg = {"test": "msg"}
        msg_dir = MessageSpecification.MSG_DIRECTION_BOTH

        msg_spec = MessageSpecification(msg_type, msg_subtype, msg, msg_url, msg_dir)

        self.MsgEx.RegisterMessageType(msg_spec)

        # Initialize the Service on the first run
        self.MsgEx.SvcInit()

        ep.MessagePut(msg, msg_type, msg_subtype)

        # Run the Service again to publish the message.
        self.MsgEx.SvcRun()

        utime.sleep(1)

        # Run the Service again to receive the message.
        self.MsgEx.SvcRun()

        recv_msg = ep.MessageGet(msg_type, msg_subtype)
        print(recv_msg)
        self.assertEqual(recv_msg[Message.MSG_SECTION_DATA], msg)

