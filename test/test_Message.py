
import sys
sys.path.append('../')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from upyiot.comm.Messaging.Message import Message
from upyiot.comm.Messaging.MessageTemplate import *
from upyiot.comm.Messaging.Parser.JsonParser import JsonParser
from upyiot.system.SystemTime.SystemTime import SystemTime

# Other
import uio
import utime

def DeviceId():
    return "123"

class test_Message(unittest.TestCase):

    # JSON representation
    MSG_SECTION_META = "meta"
    MSG_SECTION_DATA = "data"
    MSG_META_DATETIME = "dt"
    MSG_META_VERSION = "ver"
    MSG_META_TYPE = "type"
    MSG_META_SUBTYPE = "stype"
    MSG_META_ID = "id"

    TimeInstance = SystemTime.InstanceGet()

    Metadata = {
        MSG_META_DATETIME:  123,
        MSG_META_VERSION:   1,
        MSG_META_TYPE:      1,
        MSG_META_SUBTYPE:   1,
        MSG_META_ID:        DeviceId(),
    }

    MetadataFuncs = {
        MSG_META_DATETIME: TimeInstance.Epoch,
    }

    def setUp(arg):
        return

    def tearDown(arg):
        return

    def test_SerializeDeserializeRoundTrip(self):

        msg_key = "msg"
        msg_test = "test"
        dev_id = DeviceId()
        datetime = int(utime.time())
        data = {
            msg_key: msg_test,
        }
        msg_type = 1
        sub_type = 2

        MessageTemplate.SectionsSet(self.MSG_SECTION_META, self.MSG_SECTION_DATA)
        MessageTemplate.MetadataTemplateSet(test_Message.Metadata, test_Message.MetadataFuncs)

        parser = JsonParser()
        Message.SetParser(parser)

        meta = {
            self.MSG_META_TYPE:      msg_type,
            self.MSG_META_SUBTYPE:   sub_type,
        }
        buffer = Message.Serialize(data, meta)
        msg_str = buffer.getvalue().decode('utf-8')

        print("Serialized message: {}".format(msg_str))

        Message.Deserialize(str(msg_str))

        Message.Print()
        self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_META][self.MSG_META_DATETIME], datetime)
        self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_META][self.MSG_META_TYPE], msg_type)
        self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_META][self.MSG_META_SUBTYPE], sub_type)
        self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_META][self.MSG_META_ID], dev_id)
        self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_DATA][msg_key], msg_test)

    def test_SerializeDeserializeNoMetadataArgument(self):

        msg_key = "msg"
        msg_test = "test"
        dev_id = DeviceId()
        datetime = int(utime.time())
        data = {
            msg_key: msg_test,
        }

        MessageTemplate.SectionsSet(self.MSG_SECTION_META, self.MSG_SECTION_DATA)
        MessageTemplate.MetadataTemplateSet(test_Message.Metadata, test_Message.MetadataFuncs)

        parser = JsonParser()
        Message.SetParser(parser)

        buffer = Message.Serialize(data)
        msg_str = buffer.getvalue().decode('utf-8')

        print("Serialized message: {}".format(msg_str))

        Message.Deserialize(str(msg_str))

        Message.Print()
        self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_META][self.MSG_META_DATETIME], datetime)
        self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_META][self.MSG_META_TYPE], self.Metadata[self.MSG_META_TYPE])
        self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_META][self.MSG_META_SUBTYPE], self.Metadata[self.MSG_META_SUBTYPE])
        self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_META][self.MSG_META_ID], dev_id)
        self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_DATA][msg_key], msg_test)

    def test_SerializeDeserializeMultiple(self):
        MessageTemplate.SectionsSet(self.MSG_SECTION_META, self.MSG_SECTION_DATA)
        MessageTemplate.MetadataTemplateSet(test_Message.Metadata, test_Message.MetadataFuncs)

        parser = JsonParser()
        Message.SetParser(parser)

        for i in range(0, 10):

            msg_key = "msg"
            msg_test = "test"

            utime.sleep(1)

            dev_id = DeviceId()
            datetime = int(utime.time())
            data = {
                msg_key: msg_test,
            }
            msg_type = i
            sub_type = i + 1

            meta = {
                self.MSG_META_TYPE:      msg_type,
                self.MSG_META_SUBTYPE:   sub_type,
            }
            buffer = Message.Serialize(data, meta)
            msg_str = buffer.getvalue().decode('utf-8')

            print("Serialized message: {}".format(msg_str))

            Message.Deserialize(str(msg_str))

            self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_META][self.MSG_META_DATETIME], datetime)
            self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_META][self.MSG_META_TYPE], msg_type)
            self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_META][self.MSG_META_SUBTYPE], sub_type)
            self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_META][self.MSG_META_ID], dev_id)
            self.assertEqual(Message.Msg[MessageTemplate.MSG_SECTION_DATA][msg_key], msg_test)