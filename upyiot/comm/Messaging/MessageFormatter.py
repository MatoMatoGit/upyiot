from micropython import const
from upyiot.middleware.SubjectObserver.SubjectObserver import Observer
from upyiot.system.ExtLogging import ExtLogging

Log = ExtLogging.Create("MsgFmt")


class MessagePartSource:

    def __init__(self, msg_formatter_obj, key, complete_count):
        self.MsgFormatter = msg_formatter_obj
        self.Key = key
        self.Count = 0
        self.CompleteCount = complete_count

    def Put(self, data):
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
            

class MessagePartSink:

    def __init__(self, msg_formatter_obj, key, complete_count):
        self.MsgFormatter = msg_formatter_obj
        self.Key = key
        self.Count = complete_count
        self.CompleteCount = complete_count

    def Get(self, data):
        if self.Count is 0:
            self.MsgFormatter.MessagePartAdd(self.Key, data)
        else:
            self.MsgFormatter.MessagePartAppend(self.Key, data)
        self._CountDec()

    def _CountDec(self):
        self.Count -= 1
        if self.Count <= 0:
            self.Count = self.CompleteCount
            self.MsgFormatter.MessagePartFinalize()


class MessagePartObserver(MessagePartSource, Observer):

    def __init__(self, msg_formatter_obj, key, complete_count):
        super().__init__(msg_formatter_obj, key, complete_count)

    def Update(self, arg):
        self.Put(arg)


class MessagePartStream(MessagePartSource):

    def __init__(self, msg_formatter_obj, key, complete_count):
        super().__init__(msg_formatter_obj, key, complete_count)

    def write(self, data):
        self.Put(data)
        

class MessageFormatter:
    SEND_ON_CHANGE      = const(0)
    SEND_ON_COMPLETE    = const(1)

    def __init__(self, msg_ex_obj, mode, msg_spec_obj, msg_meta_dict=None):
        self.MsgOut = msg_spec_obj.DataDef.copy()
        Log.info("Definition: {}".format(self.MsgOut))
        self.Mode = mode
        self.Inputs = set()
        self.MsgType = msg_spec_obj.Type
        self.MsgSubtype = msg_spec_obj.Subtype
        self.MsgMeta = msg_meta_dict
        self.PartCount = 0
        self.MsgEx = msg_ex_obj

    def GetInputs(self):
        return self.Inputs

    def CreateObserver(self, key, count=1):
        if key not in self.MsgOut:
            return -1
        observer = MessagePartObserver(self, key, count)
        self.Inputs.add(observer)
        return observer

    def CreateStream(self, key, count=1):
        if key not in self.MsgOut:
            return -1
        stream = MessagePartStream(self, key, count)
        self.Inputs.add(stream)
        return stream

    def MessagePartAdd(self, key, value):
        Log.debug("Adding part: {}:{}".format(key, value))
        if type(self.MsgOut[key]) is list:
            if type(value) is list:
                self.MsgOut[key] = value
            else:
                self.MsgOut[key].clear()
                self.MsgOut[key].append(value)
        else:
            self.MsgOut[key] = value

    def MessagePartAppend(self, key, value):
        Log.debug("Appending part: {}:{}".format(key, value))
        # If the message value is a string, append it.
        if type(value) is str:
            self.MsgOut[key] += value
        else:
            # Append the new value to the list.
            self.MsgOut[key].append(value)

    def MessagePartFinalize(self):
        self.PartCount += 1
        self._MessageHandover()

    def _MessageHandover(self):
        # If all parts of the message have been updated, or
        # the message must be sent on any change,
        # hand over the message to the Messaging Exchange class.
        if self.PartCount is len(self.MsgOut) or \
                self.Mode is MessageFormatter.SEND_ON_CHANGE:
            Log.info("Handover to MsgEx: {}".format(self.MsgOut))
            res = self.MsgEx.MessagePut(self.MsgOut, self.MsgType,
                                           self.MsgSubtype, self.MsgMeta)

            if res is -1:
                Log.error("Message handover failed.")
            self.PartCount = 0
