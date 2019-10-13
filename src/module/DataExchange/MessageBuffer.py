from middleware.NvQueue import NvQueue

class MessageBuffer:

    MSG_STRUCT_TYPE     = const(0)
    MSG_STRUCT_SUBTYPE  = const(1)
    MSG_STRUCT_DATA     = const(2)

    MsgDataLen = 30
    MsgStructFmt = ""
    Directory = ""

    _UnPackBuffer = None

    @staticmethod
    def Configure(directory, msg_len_max):
        MessageBuffer.MsgDataLen = msg_len_max
        MessageBuffer.MsgStructFmt = "<ii" + \
                                     str(MessageBuffer.MsgDataLen) + "s"
        print("[MsgBuf] FMT: {}".format(MessageBuffer.MsgStructFmt))
        MessageBuffer.Directory = directory
        print(directory)
        MessageBuffer._UnPackBuffer = bytearray(msg_len_max)
        print(type(MessageBuffer._UnPackBuffer))

    def __init__(self, file_prefix, msg_type, msg_subtype, max_entries):
        file_path = MessageBuffer.Directory + file_prefix + str(msg_type) \
                   + "_" + str(msg_subtype)
        print("[MsgBuf] File path: {}".format(file_path))
        self.Queue = NvQueue.NvQueue(file_path, MessageBuffer.MsgStructFmt,
                                     max_entries)
        self.MsgType = msg_type
        self.MsgSubtype = msg_subtype

    def MessagePut(self, msg_string):
        if len(msg_string) > MessageBuffer.MsgDataLen:
            return -1
        print("Message string: {}".format(msg_string))
        # TODO: Use this instead when NvQueue / StructFile can utilize an external buffer.
        # ustruct.pack_into(MessageBuffer.MsgStructFmt, MessageBuffer._UnPackBuffer, 0,
        #                  self.MsgType, self.MsgSubtype, msg_string)
        return self.Queue.Push(self.MsgType, self.MsgSubtype, msg_string)

    def MessageGet(self, msg_buffer=None):
        # TODO: Use the provided message buffer to unpack the struct.
        # TODO: This must be implemented in NvQueue / StructFile.
        return self.Queue.Pop()

    def MessageCount(self):
        return self.Queue.Count

    def MaxLength(self):
        return MessageBuffer.MsgDataLen
