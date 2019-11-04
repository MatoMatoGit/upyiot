from micropython import const
from middleware.SubjectObserver.SubjectObserver import Observer


class MessagePartSource:

    def __init__(self, msg_formatter_obj, key, complete_count):
        self.MsgFormatter = msg_formatter_obj
        self.Key = key
        self.Count = 0
        self.CompleteCount = complete_count

    def MessagePart(self, data):
        if self.Count is 0:
            self.MsgFormatter.MessagePartAdd(self.Key, data)
        else:
            self.MsgFormatter.MessagePartAppend(self.Key, data)
        self._CountInc()

    def _CountInc(self):
        self.Count += 1
        if self.Count is self.CompleteCount:
            self.Count = 0
            self.MsgFormatter.MessagePartFinalize()


class MessagePartObserver(MessagePartSource, Observer):

    def __init__(self, msg_formatter_obj, key, complete_count):
        super().__init__(msg_formatter_obj, key, complete_count)

    def Update(self, arg):
        self.MessagePart(arg)


class MessagePartStream(MessagePartSource):

    def __init__(self, msg_formatter_obj, key, complete_count):
        super().__init__(msg_formatter_obj, key, complete_count)

    def write(self, data):
        self.MessagePart(data)


class MessageFormatAdapter:
    SEND_ON_CHANGE      = const(0)
    SEND_ON_COMPLETE    = const(1)

    def __init__(self, endpoint, mode, msg_spec_obj):
        self.MsgDef = msg_spec_obj.DataDef.copy()
        print("[MsgFmtAdapt] Definition: {}".format(self.MsgDef))
        self.Mode = mode
        self.Inputs = set()
        self.MsgType = msg_spec_obj.Type
        self.MsgSubtype = msg_spec_obj.Subtype
        self.PartCount = 0
        self.Endpoint = endpoint

    def CreateObserver(self, key, count=1):
        if key not in self.MsgDef:
            return -1
        observer = MessagePartObserver(self, key, count)
        self.Inputs.add(observer)
        return observer

    def CreateStream(self, key, count=1):
        if key not in self.MsgDef:
            return -1
        stream = MessagePartStream(self, key, count)
        self.Inputs.add(stream)
        return stream

    def MessagePartAdd(self, key, value):
        if type(self.MsgDef[key]) is list:
            self.MsgDef[key].clear()
            self.MsgDef[key].append(value)
        else:
            self.MsgDef[key] = value

    def MessagePartAppend(self, key, value):
        # If the message value is a string, append it.
        if type(value) is str:
            self.MsgDef[key] += value
        else:
            # Append the new value to the list.
            self.MsgDef[key].append(value)

    def MessagePartFinalize(self):
        self.PartCount += 1
        self._MessageHandover()

    def _MessageHandover(self):
        # If all parts of the message have been updated, or
        # the message must be sent on any change,
        # hand over the message to the Messaging Endpoint.
        if self.PartCount is len(self.MsgDef) or \
                self.Mode is MessageFormatAdapter.SEND_ON_CHANGE:
            print("[MsgFmtAdapt] Handover to endpoint: {}".format(self.MsgDef))
            res = self.Endpoint.MessagePut(self.MsgDef, self.MsgType,
                                           self.MsgSubtype)

            if res is -1:
                print("[MsgFmtAdapt] Error: message handover failed.")
            self.PartCount = 0
