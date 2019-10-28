import sys
sys.path.append('../upyiot/')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from module.Messaging.MessageExchange import MessageExchange
from module.Messaging.MessageExchange import Endpoint
from module.Messaging.MessageFormatAdapter import MessageFormatAdapter
from module.Messaging.MessageSpecification import MessageSpecification
from middleware.ExtLogging import ExtLogging

# Other
from module.SystemTime.SystemTime import SystemTime
from umqtt.simple import MQTTClient
import utime
from micropython import const


class LogMessage(MessageSpecification):

    TYPE        = const(1)
    SUBTYPE     = const(2)
    URL         = "<pn>/<id>/log"
    DATA_KEY_MSG  = "msg"
    DATA_DEF    = {DATA_KEY_MSG: ""}
    DIRECTION   = MessageSpecification.MSG_DIRECTION_BOTH

    def __init__(self):
        super().__init__(LogMessage.TYPE,
                         LogMessage.SUBTYPE,
                         LogMessage.DATA_DEF,
                         LogMessage.URL,
                         LogMessage.DIRECTION)


class test_ExtLoggingToBroker(unittest.TestCase):

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

    Time.Service()

    def setUp(arg):
        test_ExtLoggingToBroker.MqttClient = MQTTClient(test_ExtLoggingToBroker.ID,
                                                        test_ExtLoggingToBroker.BROKER,
                                                        test_ExtLoggingToBroker.PORT)
        test_ExtLoggingToBroker.MsgEx = MessageExchange(test_ExtLoggingToBroker.DIR,
                                                        test_ExtLoggingToBroker.MqttClient,
                                                        test_ExtLoggingToBroker.ID,
                                                        test_ExtLoggingToBroker.RETRIES)
        test_ExtLoggingToBroker.RecvMsgCount = 0
        test_ExtLoggingToBroker.RecvTopic = None
        test_ExtLoggingToBroker.RecvMsg = None

    def tearDown(arg):
        test_ExtLoggingToBroker.MsgEx.Reset()

    @staticmethod
    def MqttMsgRecvCallback(topic, msg):
        test_ExtLoggingToBroker.RecvTopic = topic
        test_ExtLoggingToBroker.RecvMsg = msg
        test_ExtLoggingToBroker.RecvMsgCount = test_ExtLoggingToBroker.RecvMsgCount + 1

    def test_PublishLogMessages(self):
        log_test_a = ["a", "info message a", "error message a"]
        log_test_b = ["b", "info message b", "error message b"]

        # Message definition
        msg_spec = LogMessage()

        # Create a Messaging Endpoint and a MessageFormatAdapter.
        ep = Endpoint()
        adapt = MessageFormatAdapter(ep, MessageFormatAdapter.SEND_ON_COMPLETE, msg_spec)

        # Create a stream for the msg field.
        log_stream = adapt.CreateStream(LogMessage.DATA_KEY_MSG, 2)

        # Configure the ExtLogging class.
        ExtLogging.ConfigGlobal(level=ExtLogging.INFO, stream=log_stream)

        # Create ExtLogger instances.
        log_a = ExtLogging.LoggerGet(log_test_a[0])
        log_b = ExtLogging.LoggerGet(log_test_b[0])

        # Register the log message type and topic.
        self.MsgEx.RegisterMessageType(msg_spec)

        # Initialize the Messaging Service on the first run
        self.MsgEx.Service()

        log_a.info(log_test_a[1])
        log_a.error(log_test_a[2])

        log_b.info(log_test_b[1])
        log_b.error(log_test_b[2])

        # Run the Service again to publish the messages.
        self.MsgEx.Service()

        utime.sleep(1)

        # Run the Service again to receive the message.
        self.MsgEx.Service()

        # Receive both published log messages.
        recv_msg = ep.MessageGet(msg_spec.Type, msg_spec.Subtype)
        print("Received message: {}".format(recv_msg))
        recv_msg = ep.MessageGet(msg_spec.Type, msg_spec.Subtype)
        print("Received message: {}".format(recv_msg))

