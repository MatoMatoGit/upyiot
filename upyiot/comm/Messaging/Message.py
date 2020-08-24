from micropython import const
from upyiot.comm.Messaging.MessageTemplate import *
import uio


class Message:

    Msg = None
    _StreamBuffer = None
    _Parser = None

    @staticmethod
    def SetParser(parser_obj):
        _Parser = parser_obj

    @staticmethod
    def DeviceId(device_id=None):
        if device_id is None:
            return Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_ID]
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_ID] = device_id

    @staticmethod
    def Message():
        return Message.Msg

    @staticmethod
    def Stream():
        return Message._StreamBuffer

    @staticmethod
    def Serialize(msg_data_dict, msg_type, msg_subtype):
        Msg = MessageTemplate.MessageTemplate()
        print("[Msg] Serializing message with metadata: {} | data: {}".format(Message.Msg[MSG_SECTION_META], msg_data_dict, msg_type, msg_subtype))
        if Message._StreamBuffer is not None:
            Message._StreamBuffer.close()
        Message._StreamBuffer = uio.BytesIO(Message.MSG_SIZE_MAX)
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_TYPE] = msg_type
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_SUBTYPE] = msg_subtype
        Message.Msg[Message.MSG_SECTION_DATA] = msg_data_dict
        _Parser.Dump(Message.Msg, Message._StreamBuffer)
        return Message._StreamBuffer

    @staticmethod
    def Deserialize(msg_str):
        try:
            Message.Msg = _Parser.Loads(msg_str)
        except ValueError:
            print("[Msg] Invalid format: {}".format(msg_str))
        return Message.Msg

    @staticmethod
    def Print():
        print(Message.Msg)