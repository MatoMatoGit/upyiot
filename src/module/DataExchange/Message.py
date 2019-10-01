from micropython import const
import ujson


class Message:
    SER_BUFFER_SIZE = const(300)

    Msg = dict()
    MSG_SECTION_META = "meta"
    MSG_SECTION_DATA = "data"
    MSG_META_DATETIME = "dt"
    MSG_META_VERSION = "ver"
    MSG_META_TYPE = "type"
    MSG_META_SUBTYPE = "stype"
    MSG_META_ID = "id"

    Msg = {
        MSG_SECTION_META: {
            MSG_META_DATETIME: "2019-09-04T23:34:44",
            MSG_META_VERSION:   1,
            MSG_META_TYPE:      1,
            MSG_META_SUBTYPE :  1,
            MSG_META_ID:        0,
        },
        MSG_SECTION_DATA: {
            # Data section is added duration serialization.
        }
    }

    @staticmethod
    def DeviceId(device_id=None):
        if device_id is None:
            return Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_ID]
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_ID] = device_id

    @staticmethod
    def Message():
        return Message.Msg

    @staticmethod
    def Serialize(datetime, msg_data_dict, msg_type, msg_subtype, stream):
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_DATETIME] = datetime
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_TYPE] = msg_type
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_SUBTYPE] = msg_subtype
        Message.Msg[Message.MSG_SECTION_DATA] = msg_data_dict
        ujson.dump(Message.Msg, stream)
        return stream

    @staticmethod
    def Deserialize(message):
        Message.Msg = ujson.loads(message)
        return Message.Msg

    @staticmethod
    def Print():
        print(Message.Msg)
