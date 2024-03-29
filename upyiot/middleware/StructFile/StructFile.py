import uos as os
import ustruct
from micropython import const


def SetLogger(logger):
    """
    Set the logger for the StructFile module.
    :param logger: Logger to use.
    :type logger: <Logger> or <ExtLogging>
    """
    global Log

    Log = logger


def ResetLogger():
    global  Log
    Log = SimpleLogger()


class SimpleLogger:

    def __int__(self):
        return

    def debug(self, string):
        print("DEBUG:StructFile:{}".format(string))

    def info(self, string):
        print("INFO:StructFile:{}".format(string))

    def error(self, string):
        print("ERROR:StructFile:{}".format(string))


Log = SimpleLogger()


def _FileCloseOnException(f, ex, raise_ex=True):
    try:
        if f is not None:
            f.close()
    except OSError:
        Log.error("File cannot be closed")
        if raise_ex is True:
            raise OSError from ex
        else:
            pass


class StructFileIterator(object):
    
    def __init__(self, struct_file_obj, index_start, index_end, num_entries):
        self.StructFile = struct_file_obj
        self.Index = index_start
        self.IndexEnd = index_end
        self.NumEntries = num_entries
        self.UserIndex = self.Index
        self.Count = 0

        Log.debug("Iterator: Opening file.")
        # Open the file and go to the offset corresponding to the start index.
        try:
            self.File = open(self.StructFile.FilePath, 'r')
            self.File.seek(self.StructFile.IndexToOffset(index_start))
            Log.debug("Iterator: Start offset: {}".format(self.File.tell()))
        except OSError as ferr:
            print("Could not access Struct file: {}".format(ferr))
            self.File = None

    def __next__(self):
        if self.File is None:
            Log.error("Iterator: No file open.")
            raise StopIteration
        try:
            self.Count = self.Count + 1
            Log.debug("Iterator: Count: {}".format(self.Count))
            Log.debug("Iterator: Index: {}".format(self.Index))
            if self.Count <= self.NumEntries:
                # Read the struct with of size DataSize from the file.
                Log.debug("Iterator: Offset: {}".format(self.File.tell()))
                Log.debug("Iterator: Reading {} bytes.".format(self.StructFile.DataSize))
                struct = self.File.read(self.StructFile.DataSize)

                # Save the current index for the user to request it.
                self.UserIndex = self.Index

                # Increment the index.
                self.Index = self.Index + 1

                # Check if the end index is reached, if so
                # reset the index.
                if self.Index > self.IndexEnd:
                    Log.debug("Iterator: Index reset")
                    self.Index = 0

                # Go to the new position in the file.
                self.File.seek(self.StructFile.IndexToOffset(self.Index))

                return ustruct.unpack(self.StructFile.DataFmt, struct)
        except OSError as ferr:
            Log.error("Iterator: Could not access Struct file: {}".format(ferr))
            _FileCloseOnException(self.File, ferr, False)

        Log.debug("Iterator: Exit.")
        # Only reached when NumEntries == Count.
        self.File.close()
        self.StructFile.Iterator = None
        raise StopIteration

    def IndexCurrent(self):
        return self.UserIndex


class StructFile(object):
    """
    The StructFile class provides storage of structures in a file.
    
    Attributes
    ----------
    DataSize : int
        Size of the structure.
    
    DataFmt : str
        String representing the format of the structure.
    
    FilePath : str
        Full path to the file containing the structures.
    
    Count : int
        Number of structures in the file.
    
    
    Methods
    -------
    WriteStruct(struct, index)
        Write a packed structure to the file at the specified
        index.
    
    WritedData(*data, index)
        Write a data tuple to the file as packed structure at the
        specified index.
    
    ReadStruct(index)
        Reads a packed structure at the specified index.
    
    ReadData(index)
        Reads a packed structure at the specified index and
        returns it as a unpacked tuple.
    
    Clear()
        Clears the structure file. The count is reset.
    
    """
    
    META_FMT    = "<II"
    META_SIZE   = 0
    FILE_OFFSET_META = const(0)

    def __init__(self, file_path, data_fmt, meta_fmt=None):
        self.DataSize = ustruct.calcsize(data_fmt)
        self.DataFmt = data_fmt
        self.UserMetaFmt = meta_fmt
        self.IteratorIndexStart = 0
        self.IteratorIndexEnd = 0
        self.IteratorCount = 0
        self.Iterator = None
        self.OffsetUserMeta = 0
        self.OffsetData = 0

        if meta_fmt is not None:
            self.UserMetaSize = ustruct.calcsize(meta_fmt)
            Log.info("User meta size: {}".format(self.UserMetaSize))
        else:
            self.UserMetaSize = 0
        self.FilePath = file_path
        Log.info("Data size: {}".format(self.DataSize))
        
        StructFile.META_SIZE = ustruct.calcsize(StructFile.META_FMT)
        StructFile.OffsetUserMeta = StructFile.META_SIZE
        self.OffsetData = self.OffsetUserMeta + self.UserMetaSize

        Log.info("Meta offset: {}".format(StructFile.FILE_OFFSET_META))
        Log.info("User meta offset: {}".format(self.OffsetUserMeta))
        Log.info("Data offset: {}".format(self.OffsetData))

        self._FileCreate()
        self._FileInit()

    def IteratorConfig(self, index_start, index_end, count=None):
        self.IteratorIndexStart = index_start
        self.IteratorIndexEnd = index_end
        if count is None:
            self.IteratorCount = index_end + 1
        else:
            self.IteratorCount = count
        Log.info("New iterator config: start: {}, stop: {}, count: {}".format(self.IteratorIndexStart,
                                                                         self.IteratorIndexEnd,
                                                                         self.IteratorCount))
    def IteratorIndex(self):
        Log.debug("Getting iterator index.")
        Log.debug(str(self.Iterator))
        return self.Iterator.IndexCurrent()

    def __iter__(self):
        self.Iterator = StructFileIterator(self, self.IteratorIndexStart,
                                           self.IteratorIndexEnd, self.IteratorCount)
        return self.Iterator

    def WriteStruct(self, index, struct):
        if len(struct) is not self.DataSize:
            Log.error("Struct size ({}) does not match expected size ({})."
                  .format(len(struct), self.DataSize))
            return -1
        
        self._FileWriteStruct(index, struct)
        return 0
        
    def WriteData(self, index, *data):
        Log.debug("Writing data [{}] {}".format(index, data))
        struct = ustruct.pack(self.DataFmt, *data)
        # print("[StructFile] Packed data: {}".format(struct))
        self.WriteStruct(index, struct)
        return 0

    def ReadStruct(self, index):
        return self._FileReadStruct(index)
   
    def ReadData(self, index):
        struct = self._FileReadStruct(index)
        if struct is None:
            return None
        try:
            data_unpacked = ustruct.unpack(self.DataFmt, struct)
            Log.debug("Read data: {}".format(data_unpacked))
            return data_unpacked
        except ValueError:
            Log.error("Data invalid.")
            return None

    def ReadMeta(self):
        meta = self._FileReadUserMetaStruct()
        if meta is None:
            return None
        try:
            meta_unpacked = ustruct.unpack(self.UserMetaFmt, meta)
            Log.debug("Read meta: {}".format(meta_unpacked))
            return meta_unpacked
        except ValueError:
            Log.error("User meta invalid.")
            return None

    def WriteMeta(self, *meta):
        Log.debug("Writing user meta: {}".format(meta))
        meta_struct = ustruct.pack(self.UserMetaFmt, *meta)
        self._FileWriteUserMetaStruct(meta_struct)
        return 0

    def Clear(self):
        self._FileDelete()
        self._FileCreate()
        self._FileInit()
        
    def Delete(self):
        self._FileDelete()

    def _FileReadMeta(self, file):
        try:
            file.seek(StructFile.FILE_OFFSET_META)
            Log.debug("Reading meta at offset: {}".format(file.tell()))
            meta = file.read(StructFile.META_SIZE)
        except OSError as ferr:
            Log.error("Could not access Struct file: {}".format(ferr))
            return -1
        
        try:
            meta_unpacked = ustruct.unpack(StructFile.META_FMT, meta)
            Log.debug("Read metadata: {}".format(meta_unpacked))
            return 0
        except ValueError:
            Log.error("Metadata invalid.")
            return -1
            
            
    def _FileWriteMeta(self, file):
        try:
            file.seek(StructFile.FILE_OFFSET_META)
            Log.debug("Writing meta at offset: {}".format(file.tell()))
            meta = ustruct.pack(StructFile.META_FMT, 0, 0)
            written = file.write(meta)
            Log.debug("Written: {}".format(written))
        except OSError as ferr:
            Log.error("Could not access Struct file: {}".format(ferr))

    def _FileReadUserMetaStruct(self):
        f = None
        try:
            f = open(self.FilePath, 'r')

            f.seek(self.OffsetUserMeta)
            Log.debug("Reading user meta struct at offset: {}".format(f.tell()))
            struct = f.read(self.UserMetaSize)
            f.close()
            return struct
        except OSError as ferr:
            Log.error("Could not access Struct file: {}".format(ferr))
            _FileCloseOnException(f, ferr)
            return None

    def _FileWriteUserMetaStruct(self, meta_struct):
        f = None
        try:
            f = open(self.FilePath, 'r+')

            f.seek(self.OffsetUserMeta)
            Log.debug("Writing user meta struct at offset: {}".format(f.tell()))
            f.write(meta_struct)

            f.close()
        except OSError as ferr:
            Log.error("Could not access Struct file: {}".format(ferr))
            _FileCloseOnException(f, ferr)

    def _FileWriteStruct(self, index, struct):
        if index < 0:
            return None
        f = None
        try:
            f = open(self.FilePath, 'r+') 
            offset = self.IndexToOffset(index)
            Log.debug("Calculated offset: {}".format(offset))
            f.seek(offset)
            Log.debug("Writing struct at offset: {}".format(f.tell()))
            written = f.write(struct)
            Log.debug("Written: {}".format(written))
            f.close()
        except OSError as ferr:
            Log.error("Could not access Struct file: {}".format(ferr))
            _FileCloseOnException(f, ferr)

    def _FileReadStruct(self, index):
        offset = self.IndexToOffset(index)
        f = None
        try:
            f = open(self.FilePath, 'r') 
            f.seek(offset)
            Log.debug("Reading struct at offset: {}".format(f.tell()))
            struct = f.read(self.DataSize)
            f.close()
            return struct
        except OSError as ferr:
            Log.error("Could not access Struct file: {}".format(ferr))
            _FileCloseOnException(f, ferr)
            return None
    
    def _FileCreate(self):
        Log.info("Creating Struct file '{}'.".format(self.FilePath))
        f = None
        try:
            f = open(self.FilePath, 'r')
            f.close()
            Log.info("Struct file already exists")
        except OSError:
            try:
                f = open(self.FilePath, 'w')
                f.close()
                Log.info("Struct file created")
            except OSError:
                Log.error("Failed to create Struct file")
                raise

    def _FileDelete(self):
        try:
            os.remove(self.FilePath)
            Log.info("Deleted Struct file")
        except OSError:
            Log.error("Failed to remove Struct file.")

    def _FileInit(self):
        f = None
        try:
            f = open(self.FilePath, 'r+') 
            if self._FileReadMeta(f) is -1:
                Log.info("Struct file is uninitialized. Initializing..")
                self._FileWriteMeta(f)
            f.close()
        except OSError as ferr:
            Log.error("Could not access Struct file: {}".format(ferr))
            _FileCloseOnException(f, ferr)

    def IndexToOffset(self, index):
        return self.OffsetData + self.DataSize * index
