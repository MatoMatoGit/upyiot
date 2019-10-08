import uerrno
import ustruct
import utime
from middleware.NvQueue import NvQueue
from Message import Message

class MessageBuffer:

    MSG_STRUCT_TYPE     = const(0)
    MSG_STRUCT_SUBTYPE  = const(1)
    MSG_STRUCT_DATA     = const(2)

    MsgDataLen = 30
    QueueLen = 10
    MsgStructFmt = "<II"
    Directory = ""

    @staticmethod
    def Configure(directory, msg_len_max, queue_len_max):
        MessageBuffer.MsgDataLen = msg_len_max
        MessageBuffer.QueueLen = queue_len_max
        MessageBuffer.MsgStructFmt = MessageBuffer.MsgStructFmt + \
                                     str(MessageBuffer.MsgDataLen) + "s"
        MessageBuffer.Directory = directory

    def __init__(self, msg_type, msg_subtype):
        file_path = MessageBuffer.Directory + "/data_snk_" + str(msg_type) \
                    + "_" + str(msg_subtype)
        self.Buffer = NvQueue.NvQueue(file_path, MessageBuffer.MSG_STRUCT_FMT,
                                      MessageBuffer.QueueLen)
        self.MsgType = msg_type
        self.MsgSubtype = msg_subtype

    def MessagePackAndPut(self, msg_data_dict, stream):
        Message.Create(utime.datetime(), msg_data_dict, self.MsgType, self.MsgSubtype)
        ustruct.pack_into(MessageBuffer.MSG_STRUCT_FMT, stream, 0,
                          self.MsgType, self.MsgSubtype, msg_data_dict)

        return ExchangeEndpoint._PackBuffer

    def MessagePut(self, msg_data_dict):
        Message.Create(utime.datetime(), msg_data_dict, msg_type, msg_subtype)
        ExchangeEndpoint.SourceMessageFile.AppendStruct(
            ExchangeEndpoint.MessagePack(msg_type, msg_subtype,
                                         Message.Serialize()))

    def MessageCount():
        return ExchangeEndpoint.SourceMessageFile.Count

    def SinkMessageFileInit(msg_type, msg_subtype):
        struct_file = StructFile(ExchangeEndpoint.Directory + "/data_snk_" + str(msg_type)
                                 + "_" + str(msg_subtype), ExchangeEndpoint.MSG_STRUCT_FMT)
        sink_msg_entry = [msg_type, msg_subtype, struct_file, 0]
        ExchangeEndpoint.SinkMessageFiles.append(sink_msg_entry)

    def _SinkMessageEntryIndexGet(msg_type, msg_subtype):
        i = 0
        for sink_msg_entry in ExchangeEndpoint.SinkMessageFiles:
            if sink_msg_entry[ExchangeEndpoint.SINK_MSG_FILE_ENTRY_TYPE] is msg_type and \
                    sink_msg_entry[ExchangeEndpoint.SINK_MSG_FILE_ENTRY_SUBTYPE] is msg_subtype:
                return i
            i = i + 1
        return None

    def _SinkMessageFileFromType(msg_type, msg_subtype):
        entry_index = ExchangeEndpoint._SinkMessageEntryIndexGet(msg_type, msg_subtype)
        return ExchangeEndpoint.SinkMessageFiles[entry_index][ExchangeEndpoint.SINK_MSG_FILE_ENTRY_FILE]

    def SinkMessageGet(msg_type, msg_subtype):
        entry_index = ExchangeEndpoint._SinkMessageEntryIndexGet(msg_type, msg_subtype)
        file = _SinkMessageFileFromType(msg_type, msg_subtype)
        read_index = ExchangeEndpoint.SinkMessageFiles[entry_index][ExchangeEndpoint.SING_MSG_FILE_ENTRY_READ_INDEX]

        if read_index >= file.Count:
            return None
        SinkMessageFiles[entry_index][ExchangeEndpoint.SING_MSG_FILE_ENTRY_READ_INDEX] = read_index + 1

    def SinkMessageCount(msg_type, msg_subtype):
        entry_index = _SinkMessageEntryIndexGet(msg_type, msg_subtype)
        file = _SinkMessageFileFromType(msg_type, msg_subtype)
        read_index = SinkMessageFiles[entry_index][SING_MSG_FILE_ENTRY_READ_INDEX]

        return file.Count - read_index
