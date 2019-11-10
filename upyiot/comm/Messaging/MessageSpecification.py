try:
    import ujson as json
except:
    import json


MSG_SPEC_KEY_TYPE       = "type"
MSG_SPEC_KEY_SUBTYPE    = "stype"
MSG_SPEC_KEY_DATA       = "data"
MSG_SPEC_KEY_URL        = "url"
MSG_SPEC_KEY_DIR        = "dir"


class MessageSpecification:

    MSG_DIRECTION_SEND = 0
    MSG_DIRECTION_RECV = 1
    MSG_DIRECTION_BOTH = 2

    URL_FIELD_DEVICE_ID = "<id>"
    URL_FIELD_PRODUCT_NAME = "<pn>"

    UrlFields = None

    def __init__(self, msg_type, msg_subtype, msg_data_def, msg_url, direction):
        self.Type = msg_type
        self.Subtype = msg_subtype
        self.DataDef = msg_data_def
        self.Url = MessageSpecification.UrlResolve(msg_url)
        self.Direction = direction

    def __str__(self):
        return "----\nMessage specification\nType:{}\nSubtype:{}" \
               "\nDataDef:{}\nUrl:{}\nDirection:{}\n----\n".format(self.Type,
                                                                   self.Subtype,
                                                                   self.DataDef,
                                                                   self.Url,
                                                                   MessageSpecification.DirectionString(self.Direction))

    @staticmethod
    def Config(url_fields):
        MessageSpecification.UrlFields = url_fields

    @staticmethod
    def UrlResolve(url):
        if MessageSpecification.UrlFields is None:
            return url
        for key in MessageSpecification.UrlFields:
            if key in url:
                url = url.replace(key,
                                  MessageSpecification.UrlFields[key])
        return url

    @staticmethod
    def DirectionString(direction):
        if direction is MessageSpecification.MSG_DIRECTION_SEND:
            return "send"
        elif direction is MessageSpecification.MSG_DIRECTION_RECV:
            return "recv"
        else:
            return "both"

    @staticmethod
    def CreateFromFile(file):

        f_in = open(file, 'r')
        json_str = f_in.read()
        f_in.close()

        spec = json.loads(json_str)
        return MessageSpecification(spec[MSG_SPEC_KEY_TYPE],
                                    spec[MSG_SPEC_KEY_SUBTYPE],
                                    spec[MSG_SPEC_KEY_DATA],
                                    spec[MSG_SPEC_KEY_URL],
                                    spec[MSG_SPEC_KEY_DIR])
