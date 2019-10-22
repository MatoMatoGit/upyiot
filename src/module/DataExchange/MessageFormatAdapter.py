from micropython import const
from middleware.SubjectObserver.SubjectObserver import Observer
from module.DataExchange.DataExchange import Endpoint


class MessagePartObserver(Observer):

    def __init__(self, msg_formatter_obj, key):
        self.MsgFormatter = msg_formatter_obj
        self.Key = key

    def Update(self, arg):
        self.MsgFormatter.MessagePartAdd(self.Key, arg)


class MessagePartStream:

    def __init__(self, msg_formatter_obj, key):
        self.MsgFormatter = msg_formatter_obj
        self.Key = key

    def write(self, data):
        self.MsgFormatter.MessagePartAdd(self.Key, data)


class MessageFormatAdapter:
    SEND_ON_CHANGE   = const(0)
    SEND_ON_COMPLETE = const(1)

    def __init__(self, msg_def, msg_type, msg_subtype, mode):
        self.MsgDef = msg_def
        self.Mode = mode
        self.Inputs = set()
        self.MsgType = msg_type
        self.MsgSubtype = msg_subtype
        self.PartCount = 0
        self.Endpoint = Endpoint()

    def CreateObserver(key):
        if key is not in self.MsgDef:
             return -1
        observer = MessagePartObserver(self, key)
        self.Inputs.add(observer)
        return observer

    def CreateStream(key):
        if key is not in self.MsgDef:
             return -1
        stream = MessagePartStream(self, key)
        self.Inputs.add(stream)
        return stream

    def MessagePartAdd(key, value)
        self.MsgDef[key] = value
        self.PartCount = self.PartCount + 1
        # If all parts of the message have been updated, or
        # the message must be sent on any change,
        # hand over the message to the DataExchange Endpoint.
        if self.PartCount is len(self.Msg) or self.Mode is MessageFormatAdapter.SEND_ON_CHANGE:
            self.Endpoint.MessagePut(self.MsgDef, self.MsgType, 
                                     self.MsgSubtype)
            self.PartCount = 0
