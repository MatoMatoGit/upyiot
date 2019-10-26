
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
