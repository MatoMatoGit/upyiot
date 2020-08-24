from micropython import const


# JSON representation
MSG_SECTION_META = "meta"
MSG_SECTION_DATA = "data"
MSG_META_DATETIME = "dt"
MSG_META_VERSION = "ver"
MSG_META_TYPE = "type"
MSG_META_SUBTYPE = "stype"
MSG_META_ID = "id"

# CBOR representation
MSG_SECTION_META = const(0)
MSG_SECTION_DATA = const(1)
MSG_META_DATETIME = const(10)
MSG_META_VERSION = const(11)
MSG_META_TYPE = const(12)
MSG_META_SUBTYPE = const(13)
MSG_META_ID = const(14)

TimeInstance = None

Metadata = {
            MSG_META_DATETIME: TimeInstance.Epoch(),
            MSG_META_VERSION:   1,
            MSG_META_TYPE:      1,
            MSG_META_SUBTYPE:   1,
            MSG_META_ID:        0,
        }

class MessageTemplate:

    MSG_SIZE_MAX = const(300)

    Msg = dict()

    @staticmethod
    def SetMetadataTemplate(metadata_dict):
        global Metadata

        Metadata = metadata_dict

    def __init__(self):

        self.Msg = {
            MSG_SECTION_META: MessageTemplate.Metadata,
            MSG_SECTION_DATA: {
                # Data section is added duration serialization.
            }
        }
