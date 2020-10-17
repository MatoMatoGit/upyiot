from upyiot.comm.Messaging.Parser.MessageParser import MessageParser
import cbor


class CborParser(MessageParser):

    def __init__(self):
        return

    def Loads(self, string_obj):
        return cbor.loads(string_obj)

    def Dumps(self, dict_obj, stream_buf):
        cbor.dump(dict_obj, stream_buf)
