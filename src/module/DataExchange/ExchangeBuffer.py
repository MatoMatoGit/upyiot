import uerrno
import ustruct
import utime
from middleware.StructFile import StructFile


MsgDataLen = 30
MsgStructFmt = "<II"
MSG_STRUCT_TYPE     = const(0)
MSG_STRUCT_SUBTYPE  = const(1)
MSG_STRUCT_DATA     = const(2)

SINK_MSG_FILE_ENTRY_TYPE    = const(0)
SINK_MSG_FILE_ENTRY_SUBTYPE = const(1)
SINK_MSG_FILE_ENTRY_FILE    = const(2)
SING_MSG_FILE_ENTRY_READ_INDEX = const(3)

Directory = ""
SourceMessageFile = None
SinkMessageFiles = []
_PackBuffer = None

def Configure(directory, msg_len_max):
    global MsgDataLen
    global MsgStructFmt
    global SourceMessageFile

    MsgDataLen = msg_len_max
    MsgStructFmt = MsgStructFmt + + str(MsgDataLen) + "s"

    if ExchangeBuffer.SourceMessageFile is None:
        Directory = directory
        SourceMessageFile = StructFile(directory + "/data_src",
                                                        ExchangeEndpoint.MSG_STRUCT_FMT)
    ExchangeEndpoint._PackBuffer = bytearray(ExchangeEndpoint.SourceMessageFile.DataSize +
                                             ExchangeEndpoint.MSG_DATA_LEN_MAX)

def MessagePack(msg_type, msg_subtype, msg_data):
    ustruct.pack_into(ExchangeEndpoint.MSG_STRUCT_FMT, ExchangeEndpoint._PackBuffer, 0,
                      msg_type, msg_subtype, msg_data)
    return ExchangeEndpoint._PackBuffer

def SourceMessagePut(msg_data_dict, msg_type, msg_subtype):
    Message.Create(utime.datetime(), msg_data_dict, msg_type, msg_subtype)
    ExchangeEndpoint.SourceMessageFile.AppendStruct(
        ExchangeEndpoint.MessagePack(msg_type, msg_subtype,
                                     Message.Serialize()))

def SourceMessageCount():
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
