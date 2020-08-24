from upyiot.comm.Messaging.Parser.MessageParser import MessageParser
import cbor


class CborParser(MessageParser):

    def __init__():
        return

    def Loads(string_obj):
        return cbor.loads(string_obj)

    def Dumps(dict_obj, stream_buf):
        cbor.dump(dict_obj, stream_buf)