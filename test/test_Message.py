
import sys
sys.path.append('../src/')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from module.DataExchange.Message import Message

# Other
import uio

class test_Message(unittest.TestCase):


    def setUp(arg):
        return

    def tearDown(arg):
        return

    def test_DeviceIdSet(self):
        id_set = 0x200

        Message.DeviceId(id_set)

        self.assertEqual(Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_ID], id_set)

    def test_DeviceIdGet(self):
        id_set = 0x200

        Message.DeviceId(id_set)
        id_get = Message.DeviceId()

        self.assertEqual(id_set, id_get)
        Message.Print()

    def test_SerializeDeserializeRoundTrip(self):
        buffer = uio.BytesIO(Message.SER_BUFFER_SIZE)
        msg_key = "msg"
        msg_test = "test"
        id = 0x200
        datetime = '2019-10-01T23:00:00'
        data = {
            msg_key: msg_test,
        }
        type = 1
        sub_type = 2

        Message.DeviceId(id)

        buffer = Message.Serialize(datetime, data, type, sub_type, buffer)
        msg_str = buffer.getvalue().decode('utf-8')

        print(msg_str)

        Message.Deserialize(msg_str)

        Message.Print()
        self.assertEqual(Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_DATETIME], datetime)
        self.assertEqual(Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_TYPE], type)
        self.assertEqual(Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_SUBTYPE], sub_type)
        self.assertEqual(Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_ID], id)
        self.assertEqual(Message.Msg[Message.MSG_SECTION_DATA][msg_key], msg_test)



