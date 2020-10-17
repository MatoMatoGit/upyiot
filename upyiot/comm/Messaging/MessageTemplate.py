from micropython import const


class MessageTemplate:

    # JSON representation
    MSG_SECTION_META = ""
    MSG_SECTION_DATA = ""
    Metadata = None
    MetadataFunctions = None

    MSG_SIZE_MAX = const(300)

    @staticmethod
    def SectionsSet(meta_section_key, data_section_key):
        MessageTemplate.MSG_SECTION_META = meta_section_key
        MessageTemplate.MSG_SECTION_DATA = data_section_key
        print("[MsgTemp] Section keys: {}".format((MessageTemplate.MSG_SECTION_META,
            MessageTemplate.MSG_SECTION_DATA)))


    @staticmethod
    def MetadataTemplateSet(metadata_dict, metadata_funcs=None):
        MessageTemplate.Metadata = metadata_dict
        MessageTemplate.MetadataFunctions = metadata_funcs
        print("[MsgTemp] Metadata set: {}".format(MessageTemplate.Metadata))

    def __init__(self):
        if self.MetadataFunctions is not None:
            for key in self.MetadataFunctions.keys():
                if key in self.Metadata.keys():
                    self.Metadata[key] = self.MetadataFunctions[key]()

        self.Msg = {
            self.MSG_SECTION_META: self.Metadata,
            self.MSG_SECTION_DATA: {
                # Data section is added duration serialization.
            },
        }
        print("[MsgTemp]: {}".format(self.Msg))