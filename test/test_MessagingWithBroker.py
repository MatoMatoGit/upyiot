import sys
sys.path.append('../upyiot/')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from module.Messaging.MessageExchange import MessageExchange
from module.Messaging.MessageExchange import Endpoint
from module.Messaging.MessageSpecification import MessageSpecification

# Other
from module.Messaging.Message import Message
from module.SystemTime.SystemTime import SystemTime
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

    Time.Service()

    def setUp(arg):
        test_MessagingWithBroker.RecvMsgCount = 0
        test_MessagingWithBroker.RecvTopic = None
        test_MessagingWithBroker.RecvMsg = None
        test_MessagingWithBroker.MqttClient = MQTTClient(test_MessagingWithBroker.ID,
                                                         test_MessagingWithBroker.BROKER,
                                                         test_MessagingWithBroker.PORT)
        test_MessagingWithBroker.MsgEx = MessageExchange(test_MessagingWithBroker.DIR,
                                                         test_MessagingWithBroker.MqttClient,
                                                         test_MessagingWithBroker.ID,
                                                         test_MessagingWithBroker.RETRIES)

    def tearDown(arg):
        test_MessagingWithBroker.MsgEx.Reset()

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
        self.MsgEx.Service()

        ep.MessagePut(msg, msg_type, msg_subtype)

        # Run the Service again to publish the message.
        self.MsgEx.Service()

        utime.sleep(1)

        # Run the Service again to receive the message.
        self.MsgEx.Service()

        recv_msg = ep.MessageGet(msg_type, msg_subtype)
        print(recv_msg)
        self.assertEqual(recv_msg[Message.MSG_SECTION_DATA], msg)

