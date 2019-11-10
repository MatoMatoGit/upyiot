import sys
sys.path.append('../')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from upyiot.comm.Messaging.MessageExchange import MessageExchange
from upyiot.comm.Messaging.MessageExchange import Endpoint
from upyiot.comm.Messaging.MessageFormatAdapter import MessageFormatAdapter
from upyiot.comm.Messaging.MessageSpecification import MessageSpecification
from upyiot.system.ExtLogging import ExtLogging

# Other
from upyiot.system.SystemTime.SystemTime import SystemTime
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
    UrlFields = {MessageSpecification.URL_FIELD_DEVICE_ID: ID,
                 MessageSpecification.URL_FIELD_PRODUCT_NAME: "smartsensor"}

    Time.SvcRun()

    def setUp(self):
        MessageSpecification.Config(self.UrlFields)
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
        log_stream = adapt.CreateStream(LogMessage.DATA_KEY_MSG, ExtLogging.WRITES_PER_LOG)

        # Configure the ExtLogging class.
        ExtLogging.ConfigGlobal(level=ExtLogging.INFO, stream=log_stream)

        # Create ExtLogger instances.
        log_a = ExtLogging.LoggerGet(log_test_a[0])
        log_b = ExtLogging.LoggerGet(log_test_b[0])

        # Register the log message type and topic.
        self.MsgEx.RegisterMessageType(msg_spec)

        # Initialize the Messaging Service on the first run
        self.MsgEx.SvcInit()

        log_a.info(log_test_a[1])
        log_a.error(log_test_a[2])

        log_b.info(log_test_b[1])
        log_b.error(log_test_b[2])

        # Run the Service again to publish the messages.
        self.MsgEx.SvcRun()

        utime.sleep(1)

        # Run the Service again to receive the message.
        self.MsgEx.SvcRun()

        # Receive both published log messages.
        recv_msg = ep.MessageGet(msg_spec.Type, msg_spec.Subtype)
        print("Received message: {}".format(recv_msg))
        recv_msg = ep.MessageGet(msg_spec.Type, msg_spec.Subtype)
        print("Received message: {}".format(recv_msg))

