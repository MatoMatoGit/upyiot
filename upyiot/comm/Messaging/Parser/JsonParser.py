from upyiot.comm.Messaging.Parser.MessageParser import MessageParser
import ujson


class JsonParser(MessageParser):

    def __init__():
        return

    def Loads(string_obj):
        return ujson.loads(string_obj)

    def Dumps(dict_obj, stream_buf):
        ujson.dump(dict_obj, stream_buf)