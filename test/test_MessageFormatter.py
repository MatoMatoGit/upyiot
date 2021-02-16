import sys
sys.path.append('../')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from upyiot.comm.Messaging.MessageFormatter import MessageFormatter

# Other
from ExampleMessage import ExampleMessage


class MsgExStub:

    def __init__(self):
        self.Data = None
        self.Meta = None
        self.Type = 0
        self.SubType = 0
        return

    def GetLastMessage(self):
        return self.Data

    def ResetLastMessage(self):
        self.Data = None

    def MessagePut(self, msg_data_dict, msg_type, msg_subtype, msg_meta_dict=None):
        self.Data = msg_data_dict.copy()
        self.Type = msg_type
        self.SubType = msg_subtype
        self.Meta = msg_meta_dict
        print("[MsgExStub] Put message of type {}.{}: {} ".format(msg_type, msg_subtype, msg_data_dict))

    def MessageGet(self, msg_type, msg_subtype):
        print("[MsgExStub] Getting message")


class test_MessageFormatter(unittest.TestCase):

    def setUp(arg):
        return

    def tearDown(arg):
        return

    def test_SendOnChange(self):
        msg_spec = ExampleMessage()

        msg_ex = MsgExStub()
        fmt = MessageFormatter(msg_ex, MessageFormatter.SEND_ON_CHANGE, msg_spec)

        observer = fmt.CreateObserver(ExampleMessage.DATA_KEY_N)
        stream = fmt.CreateStream(ExampleMessage.DATA_KEY_ARRAY)

        inputs = fmt.GetInputs()
        print("Formatter inputs: {}".format(inputs))
        self.assertEqual(len(inputs), 2)

        observer.Update(3)

        data = msg_ex.GetLastMessage()
        print("Data from MsgExStub: {}".format(data))
        self.assertEqual(data[ExampleMessage.DATA_KEY_N], 3)
        self.assertEqual(data[ExampleMessage.DATA_KEY_ARRAY], [])

        stream.write([1, 2, 3])

        data = msg_ex.GetLastMessage()
        print("Data from MsgExStub: {}".format(data))
        self.assertEqual(data[ExampleMessage.DATA_KEY_N], 3)
        self.assertEqual(data[ExampleMessage.DATA_KEY_ARRAY], [1, 2, 3])

        observer.Update(4)

        data = msg_ex.GetLastMessage()
        print("Data from MsgExStub: {}".format(data))
        self.assertEqual(data[ExampleMessage.DATA_KEY_N], 4)
        self.assertEqual(data[ExampleMessage.DATA_KEY_ARRAY], [1, 2, 3])

        stream.write([1, 2, 3, 4])

        data = msg_ex.GetLastMessage()
        print("Data from MsgExStub: {}".format(data))
        self.assertEqual(data[ExampleMessage.DATA_KEY_N], 4)
        self.assertEqual(data[ExampleMessage.DATA_KEY_ARRAY], [1, 2, 3, 4])

    def test_SendOnChangeVariation(self):
        msg_spec = ExampleMessage()

        msg_ex = MsgExStub()
        fmt = MessageFormatter(msg_ex, MessageFormatter.SEND_ON_CHANGE, msg_spec)

        stream = fmt.CreateStream(ExampleMessage.DATA_KEY_N)
        observer = fmt.CreateObserver(ExampleMessage.DATA_KEY_ARRAY)

        inputs = fmt.GetInputs()
        print("Formatter inputs: {}".format(inputs))
        self.assertEqual(len(inputs), 2)

        observer.Update([2, 3])
        stream.write(1)

        data = msg_ex.GetLastMessage()
        print("Data from MsgExStub: {}".format(data))
        self.assertEqual(data[ExampleMessage.DATA_KEY_N], 1)
        self.assertEqual(data[ExampleMessage.DATA_KEY_ARRAY], [2, 3])

        stream.write(2)
        observer.Update([4, 5])

        data = msg_ex.GetLastMessage()
        print("Data from MsgExStub: {}".format(data))
        self.assertEqual(data[ExampleMessage.DATA_KEY_N], 2)
        self.assertEqual(data[ExampleMessage.DATA_KEY_ARRAY], [4, 5])

        stream.write(3)
        observer.Update([6, 7])

        data = msg_ex.GetLastMessage()
        print("Data from MsgExStub: {}".format(data))
        self.assertEqual(data[ExampleMessage.DATA_KEY_N], 3)
        self.assertEqual(data[ExampleMessage.DATA_KEY_ARRAY], [6, 7])

        stream.write(4)
        observer.Update([1, 2, 3, 4])

        data = msg_ex.GetLastMessage()
        print("Data from MsgExStub: {}".format(data))
        self.assertEqual(data[ExampleMessage.DATA_KEY_N], 4)
        self.assertEqual(data[ExampleMessage.DATA_KEY_ARRAY], [1, 2, 3, 4])

    def test_SendOnComplete(self):
        msg_spec = ExampleMessage()

        msg_ex = MsgExStub()
        fmt = MessageFormatter(msg_ex, MessageFormatter.SEND_ON_COMPLETE, msg_spec)

        observer = fmt.CreateObserver(ExampleMessage.DATA_KEY_N)
        stream = fmt.CreateStream(ExampleMessage.DATA_KEY_ARRAY)

        inputs = fmt.GetInputs()
        print("Formatter inputs: {}".format(inputs))

        observer.Update(3)

        data = msg_ex.GetLastMessage()
        self.assertEqual(data, None)

        stream.write([1, 2, 3])

        data = msg_ex.GetLastMessage()
        print("Data from MsgExStub: {}".format(data))
        self.assertEqual(data[ExampleMessage.DATA_KEY_N], 3)
        self.assertEqual(data[ExampleMessage.DATA_KEY_ARRAY], [1, 2, 3])

        msg_ex.ResetLastMessage()

        observer.Update(4)

        data = msg_ex.GetLastMessage()
        self.assertEqual(data, None)

        stream.write([1, 2, 3, 4])

        data = msg_ex.GetLastMessage()
        print("Data from MsgExStub: {}".format(data))
        self.assertEqual(data[ExampleMessage.DATA_KEY_N], 4)
        self.assertEqual(data[ExampleMessage.DATA_KEY_ARRAY], [1, 2, 3, 4])

        msg_ex.ResetLastMessage()

        observer.Update(5)

        data = msg_ex.GetLastMessage()
        self.assertEqual(data, None)

        stream.write([5, 6, 7, 8])

        data = msg_ex.GetLastMessage()
        print("Data from MsgExStub: {}".format(data))
        self.assertEqual(data[ExampleMessage.DATA_KEY_N], 5)
        self.assertEqual(data[ExampleMessage.DATA_KEY_ARRAY], [5, 6, 7, 8])

        return

    def test_SendOnCompleteAppend(self):
        msg_spec = ExampleMessage()

        msg_ex = MsgExStub()
        fmt = MessageFormatter(msg_ex, MessageFormatter.SEND_ON_COMPLETE, msg_spec)

        observer = fmt.CreateObserver(ExampleMessage.DATA_KEY_N)
        stream = fmt.CreateStream(ExampleMessage.DATA_KEY_ARRAY, 3)

        inputs = fmt.GetInputs()
        print("Formatter inputs: {}".format(inputs))

        observer.Update(3)
        stream.write(1)
        stream.write(2)
        stream.write(3)

        data = msg_ex.GetLastMessage()
        print("Data from MsgExStub: {}".format(data))
        self.assertEqual(data[ExampleMessage.DATA_KEY_N], 3)
        self.assertEqual(data[ExampleMessage.DATA_KEY_ARRAY], [1, 2, 3])

        observer.Update(4)
        stream.write(4)
        stream.write(5)
        stream.write(6)

        data = msg_ex.GetLastMessage()
        print("Data from MsgExStub: {}".format(data))
        self.assertEqual(data[ExampleMessage.DATA_KEY_N], 4)
        self.assertEqual(data[ExampleMessage.DATA_KEY_ARRAY], [4, 5, 6])

        return
