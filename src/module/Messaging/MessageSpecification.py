import ujson

MSG_SPEC_KEY_TYPE       = "type"
MSG_SPEC_KEY_SUBTYPE    = "stype"
MSG_SPEC_KEY_DATA       = "data"
MSG_SPEC_KEY_URL        = "url"
MSG_SPEC_KEY_DIR        = "dir"


class MessageSpecification:

    def __init__(self, msg_type, msg_subtype, msg_data_def, msg_url, direction):
        self.Type = msg_type
        self.Subtype = msg_subtype
        self.DataDef = msg_data_def
        self.Url = msg_url
        self.Direction = direction

    def __str__(self):
        return "----\nMessage specification\nType:{}\nSubtype:{}" \
               "\nDataDef:{}\nUrl:{}\nDirection:{}\n----\n".format(self.Type,
                                                                   self.Subtype,
                                                                   self.DataDef,
                                                                   self.Url,
                                                                   self.Direction)

def CreateFromFile(file):

    f_in = open(file, 'r')
    json = f_in.read()
    f_in.close()

    spec = ujson.loads(json)
    return MessageSpecification(spec[MSG_SPEC_KEY_TYPE],
                                spec[MSG_SPEC_KEY_SUBTYPE],
                                spec[MSG_SPEC_KEY_DATA],
                                spec[MSG_SPEC_KEY_URL],
                                spec[MSG_SPEC_KEY_DIR])
