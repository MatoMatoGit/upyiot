import uos as os
import ustruct
from micropython import const

class StructFileIterator(object):
    
    def __init__(self, struct_file_obj):
        self.StructFile = struct_file_obj
        self.Index = 0
        print("[Iterator] Opening file.")
        try:
            self.File = open(self.StructFile.FilePath, 'r')
            self.File.seek(self.StructFile.FILE_OFFSET_DATA)
            print("[Iterator] Offset: {}".format(self.File.tell()))
        except OSError as ferr:
            print("Could not access Struct file: {}".format(ferr))
            try:
                self.File.close()
                print("File closed after exception")
            except:
                pass
            finally:
                self.File = None

    def __next__(self):
        if self.File is None:
            print("[Iterator] No file open.")
            raise StopIteration
        try:
            print("[Iterator] Index: {}".format(self.Index))
            if self.Index < self.StructFile.Count:
                print("[Iterator] Offset: {}".format(self.File.tell()))
                struct = self.File.read(self.StructFile.DataSize)
                self.Index = self.Index + 1
                return ustruct.unpack(self.StructFile.DataFmt, struct)
        except OSError as ferr:
            print("Could not access Struct file: {}".format(ferr))
            try:
                self.File.close()
                print("File closed after exception")
            except:
                pass
        
        self.File.close()
        raise StopIteration
            

class StructFile(object):
    """
    The StructFile class that provides storage of structures in a file.
    
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
    AppendStruct(struct)
        Appends a packed structure to the file.
    
    AppendData(*data)
        Appends unpacked data to the file as packed structure.
    
    ReadStruct(index)
        Reads a packed structure at the specified index.
    
    ReadData(index)
        Reads a packed structure at the specified index and
        returns it as a unpacked tuple.
    
    Clear()
        Clears the structure file. The count is reset.
    
    """
    
    META_FMT    = "<HH"
    META_SIZE   = 0
    FILE_OFFSET_META = const(0)
    FILE_OFFSET_DATA = 0
    
    def __init__(self, file_path, data_fmt):
        self.DataSize = ustruct.calcsize(data_fmt)
        self.DataFmt = data_fmt
        self.FilePath = file_path
        print("Data size: {}".format(self.DataSize))
        
        self._WriteOffset = 0
        self.Count = 0
        
        StructFile.META_SIZE = ustruct.calcsize(StructFile.META_FMT)
        StructFile.FILE_OFFSET_DATA = StructFile.META_SIZE
        
        self._FileCreate()
        self._FileInit()

    def __iter__(self):
        return StructFileIterator(self)

    def AppendStruct(self, struct):
        if len(struct) is not self.DataSize:
            print("Struct size ({}) does not match expected size ({})."
                  .format(len(struct), self.DataSize))
            return -1
        
        self._FileAppendStruct(struct)
        return self.Count
        
    def AppendData(self, *data):
        struct = ustruct.pack(self.DataFmt, *data);
        self._FileAppendStruct(struct)
        
        return self.Count
    
    def ReadStruct(self, index):
        return self._FileReadStruct(index)
   
    def ReadData(self, index):
        struct = self._FileReadStruct(index)
        if struct is None:
            return None
        return ustruct.unpack(self.DataFmt, struct)
    
    def ReadDataInto(self, index, buf):
        struct = self._FileReadStruct(index)
        ustruct.unpackinto(self.DataFmt, struct, buf)
    
    def Clear(self):
        self._FileDelete()
        self._FileCreate()
        self._FileInit()
        
    def Delete(self):
        self._FileDelete()
        
    
    def _FileReadMeta(self, file):
        try:
            file.seek(StructFile.FILE_OFFSET_META)
            print("Reading meta at offset: {}".format(file.tell()))
            meta = file.read(StructFile.META_SIZE)
        except OSError as ferr:
            print("Could not access Struct file: {}".format(ferr))
            self.Count = 0
            self._WriteOffset = 0
            return -1
        
        try:
            meta_unpacked = ustruct.unpack(StructFile.META_FMT, meta)
            self.Count = meta_unpacked[0]
            self._WriteOffset = meta_unpacked[1]
            print("Read metadata: {}".format(meta_unpacked))
            return 0
        except ValueError:
            print("Metadata invalid.");
            self.Count = 0
            self._WriteOffset = 0
            return -1;
            
            
    def _FileWriteMeta(self, file):
        try:
            file.seek(StructFile.FILE_OFFSET_META)
            print("Writing meta at offset: {}".format(file.tell()))
            meta = ustruct.pack(StructFile.META_FMT, self.Count, self._WriteOffset)
            written = file.write(meta)
            print("Written: {}".format(written))
        except OSError as ferr:
            print("Could not access Struct file: {}".format(ferr))
            
    def _FileAppendStruct(self, struct):
        """ Append a formatted struct to the file. 
        """
        try:           
            f = open(self.FilePath, 'r+') 
            
            f.seek(self._WriteOffset)
            print("Writing struct at offset: {}".format(f.tell()))
            written = f.write(struct)
            print("Written: {}".format(written))
            
            self._WriteOffset += self.DataSize
            print("New write offset: {}".format(self._WriteOffset))
            self.Count = self.Count + 1
            print("Struct count: {}".format(self.Count))
            self._FileWriteMeta(f)
            
            f.close()
        except OSError as ferr:
            print("Could not access Struct file: {}".format(ferr))
            try:
                f.close()
                print("File closed after exception")
            except:
                pass     
    
    
    def _FileReadStruct(self, index):
        if index > self.Count - 1:
            return None
        try:           
            f = open(self.FilePath, 'r') 
            
            f.seek(StructFile.FILE_OFFSET_DATA + self.DataSize * index)
            print("Reading struct at offset: {}".format(f.tell()))
            struct = f.read(self.DataSize)    
            f.close()
            return struct
        except OSError as ferr:
            print("Could not access Struct file: {}".format(ferr))
            try:
                f.close()
                print("File closed after exception")
            except:
                pass
    
    def _FileCreate(self):
        try:
            f = open(self.FilePath, 'r')
            f.close()
            print("Struct file already exists")
        except OSError:
            try:
                f = open(self.FilePath, 'w')
                f.close()
                print("Struct file created")
            except OSError:
                print("Failed to create Struct file")
                
    
    def _FileDelete(self):
        try:
            os.remove(self.FilePath)
        except OSError:
            print("Failed to remove Struct file.")

    def _FileInit(self):
        try:
            f = open(self.FilePath, 'r+') 
            if self._FileReadMeta(f) is -1:
                print("Struct file is uninitialized. Initializing..")
                self._WriteOffset = StructFile.FILE_OFFSET_DATA
                self.Count = 0
                self._FileWriteMeta(f)
            f.close()
        except OSError as ferr:
            print("Could not access Struct file: {}".format(ferr))
            try:
                f.close()
                print("File closed after exception")
            except:
                pass 
