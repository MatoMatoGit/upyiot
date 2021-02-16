from micropython import const
from upyiot.comm.Messaging.MessageTemplate import MessageTemplate
from upyiot.system.ExtLogging import ExtLogging
import uio


class Message:

    Msg = None
    _StreamBuffer = None
    _Parser = None
    Log = ExtLogging.Create("Msg")

    @staticmethod
    def SetParser(parser_obj):
        Message._Parser = parser_obj
        Message.Log.debug("Parser set: {}".format(Message._Parser))

    @staticmethod
    def Message():
        return Message.Msg

    @staticmethod
    def Stream():
        return Message._StreamBuffer

    @staticmethod
    def Serialize(data_dict, meta_dict=None):
        # Create a message from the template.
        Message.Msg = MessageTemplate()
        Message.Msg = Message.Msg.Msg
        Message.Log.debug("Serializing message with metadata: {} | data: {}"
            .format(meta_dict, data_dict))
        # Close the previous stream if there is one.
        if Message._StreamBuffer is not None:
            Message._StreamBuffer.close()
        Message._StreamBuffer = uio.BytesIO(MessageTemplate.MsgSizeMax)
        # If metadata was given, check for matching keys and copy the values.
        if meta_dict is not None:
            for key in Message.Msg[MessageTemplate.MSG_SECTION_META].keys():
                if key in meta_dict.keys():
                    Message.Msg[MessageTemplate.MSG_SECTION_META][key] = meta_dict[key]
        # Copy the data dictionary.
        Message.Msg[MessageTemplate.MSG_SECTION_DATA] = data_dict
        # Serialize the message using the parser.
        Message._Parser.Dumps(Message.Msg, Message._StreamBuffer)
        return Message._StreamBuffer

    @staticmethod
    def Deserialize(msg_str):
        try:
            Message.Msg = Message._Parser.Loads(msg_str)
        except ValueError:
            Message.Log.error("Invalid format: {}".format(msg_str))
        return Message.Msg

    @staticmethod
    def Print():
        Message.Log.info(Message.Msg)
