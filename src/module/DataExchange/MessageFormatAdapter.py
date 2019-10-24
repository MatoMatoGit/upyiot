from micropython import const
from middleware.SubjectObserver.SubjectObserver import Observer


class MessagePartSource:

    def __init__(self, msg_formatter_obj, key):
        self.MsgFormatter = msg_formatter_obj
        self.Key = key


class MessagePartObserver(MessagePartSource, Observer):

    def __init__(self, msg_formatter_obj, key):
        super().__init__(msg_formatter_obj, key)

    def Update(self, arg):
        self.MsgFormatter.MessagePartAdd(self.Key, arg)


class MessagePartStream(MessagePartSource):

    def __init__(self, msg_formatter_obj, key):
        super().__init__(msg_formatter_obj, key)

    def write(self, data):
        self.MsgFormatter.MessagePartAdd(self.Key, data)


class MessageFormatAdapter:
    SEND_ON_CHANGE      = const(0)
    SEND_ON_COMPLETE    = const(1)

    def __init__(self, endpoint, msg_def, msg_type, msg_subtype, mode):
        self.MsgDef = msg_def
        self.Mode = mode
        self.Inputs = set()
        self.MsgType = msg_type
        self.MsgSubtype = msg_subtype
        self.PartCount = 0
        self.Endpoint = endpoint

    def CreateObserver(self, key):
        if key not in self.MsgDef:
            return -1
        observer = MessagePartObserver(self, key)
        self.Inputs.add(observer)
        return observer

    def CreateStream(self, key):
        if key not in self.MsgDef:
            return -1
        stream = MessagePartStream(self, key)
        self.Inputs.add(stream)
        return stream

    def MessagePartAdd(self, key, value):
        self.MsgDef[key] = value

        self.PartCount = self.PartCount + 1
        # If all parts of the message have been updated, or
        # the message must be sent on any change,
        # hand over the message to the DataExchange Endpoint.
        if self.PartCount is len(self.MsgDef) or \
                self.Mode is MessageFormatAdapter.SEND_ON_CHANGE:
            print("Handover to endpoint: {}".format(self.MsgDef))
            res = self.Endpoint.MessagePut(self.MsgDef, self.MsgType,
                                           self.MsgSubtype)
            if res is -1:
                print("Error: message handover failed.")
            self.PartCount = 0
