from micropython import const
import ujson
import uio


class Message:
    MSG_SIZE_MAX = const(300)

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
            MSG_META_SUBTYPE:   1,
            MSG_META_ID:        0,
        },
        MSG_SECTION_DATA: {
            # Data section is added duration serialization.
        }
    }

    _StreamBuffer = uio.BytesIO(MSG_SIZE_MAX)

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
    def Serialize(datetime, msg_data_dict, msg_type, msg_subtype):
        Message._StreamBuffer.seek(0)
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_DATETIME] = datetime
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_TYPE] = msg_type
        Message.Msg[Message.MSG_SECTION_META][Message.MSG_META_SUBTYPE] = msg_subtype
        Message.Msg[Message.MSG_SECTION_DATA] = msg_data_dict
        ujson.dump(Message.Msg, Message._StreamBuffer)
        return Message._StreamBuffer

    @staticmethod
    def Deserialize(msg_str):
        del Message.Msg[Message.MSG_SECTION_DATA]
        try:
            Message.Msg = ujson.loads(msg_str)
        except ValueError:
            print("Invalid JSON string: {}".format(msg_str))
        return Message.Msg

    @staticmethod
    def Print():
        print(Message.Msg)
