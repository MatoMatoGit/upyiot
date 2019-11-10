import sys
sys.path.append('../')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from upyiot.comm.Messaging.MessageBuffer import MessageBuffer

# Other


class test_MessageBuffer(unittest.TestCase):

    DIR = "./"
    MSG_LEN = 40

    MsgBuf = None

    def setUp(arg):
        return

    def tearDown(arg):
        return

    def test_Configure(self):
        MessageBuffer.Configure(test_MessageBuffer.DIR, test_MessageBuffer.MSG_LEN)

        self.assertEqual(MessageBuffer.Directory, test_MessageBuffer.DIR)
        self.assertIsNotNone(MessageBuffer._UnPackBuffer)

    def test_Constructor(self):
        MessageBuffer.Configure(test_MessageBuffer.DIR, test_MessageBuffer.MSG_LEN)

        self.MsgBuf = MessageBuffer("test", 1, 2, 30)

        self.assertIsNotNone(self.MsgBuf.Queue)
        self.assertEqual(self.MsgBuf.Queue.Space(), 30)

        self.MsgBuf.Queue.Delete()

    def test_MessagePutStringTooLong(self):
        MessageBuffer.Configure(test_MessageBuffer.DIR, test_MessageBuffer.MSG_LEN)

        test_str = "x" * (self.MSG_LEN + 1)
        res = self.MsgBuf.MessagePut(test_str)

        self.assertEqual(res, -1)

        self.MsgBuf.Queue.Delete()

    def test_MessagePutStringMaxLength(self):
        MessageBuffer.Configure(test_MessageBuffer.DIR, test_MessageBuffer.MSG_LEN)
        self.MsgBuf = MessageBuffer("test", 1, 2, 30)

        test_str = "x" * self.MSG_LEN
        res = self.MsgBuf.MessagePut(test_str)

        self.assertEqual(res, 1)

        self.MsgBuf.Queue.Delete()

    def test_MessagePutStringMaxEntries(self):

        MessageBuffer.Configure(test_MessageBuffer.DIR, test_MessageBuffer.MSG_LEN)
        self.MsgBuf = MessageBuffer("test", 1, 2, 30)

        test_str = "x" * self.MSG_LEN
        for i in range(0, 30):
            res = self.MsgBuf.MessagePut(test_str)
            self.assertEqual(res, i+1)

        self.MsgBuf.Queue.Delete()

    def test_MessagePutGetSingle(self):
        MessageBuffer.Configure(test_MessageBuffer.DIR, test_MessageBuffer.MSG_LEN)
        self.MsgBuf = MessageBuffer("test", 1, 2, 30)

        test_str = "x" * self.MSG_LEN
        self.MsgBuf.MessagePut(test_str)

        msg = self.MsgBuf.MessageGet()
        msg_str = msg[MessageBuffer.MSG_STRUCT_DATA].decode('utf-8')
        print(msg_str)

        self.assertEqual(test_str, msg_str)
        self.assertEqual(1, msg[MessageBuffer.MSG_STRUCT_TYPE])
        self.assertEqual(2, msg[MessageBuffer.MSG_STRUCT_SUBTYPE])

        self.MsgBuf.Queue.Delete()

    def test_MessagePutGetStringMaxEntries(self):

        MessageBuffer.Configure(test_MessageBuffer.DIR, test_MessageBuffer.MSG_LEN)
        self.MsgBuf = MessageBuffer("test", 1, 2, 30)

        for i in range(0, 30):

            test_str = str(i % 10) * self.MSG_LEN
            self.MsgBuf.MessagePut(test_str)

            msg = self.MsgBuf.MessageGet()
            msg_str = msg[MessageBuffer.MSG_STRUCT_DATA].decode('utf-8')
            print(msg_str)

            self.assertEqual(test_str, msg_str)

        self.MsgBuf.Queue.Delete()
