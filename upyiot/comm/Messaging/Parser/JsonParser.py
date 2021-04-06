from upyiot.comm.Messaging.Parser.MessageParser import MessageParser
import ujson


class JsonParser(MessageParser):
    def __init__(self):
        return

    def Loads(self, string_obj):
        return ujson.loads(string_obj)

    def Dumps(self, dict_obj, stream_buf):
        print(dict_obj)
        ujson.dump(dict_obj, stream_buf)
