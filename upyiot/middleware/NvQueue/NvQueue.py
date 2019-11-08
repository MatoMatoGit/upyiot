from upyiot.middleware.StructFile import StructFile
from micropython import const


class NvQueueIterator(object):

    def __init__(self, nvqueue_obj):
        print(nvqueue_obj)
        nvqueue_obj.Queue.IteratorConfig(nvqueue_obj.ReadOffset,
                                         nvqueue_obj.WriteOffset, nvqueue_obj.Count)
        self.Iterator = iter(nvqueue_obj.Queue)

    def __next__(self):
        return self.Iterator.__next__()


class NvQueue:

    # Capacity, count, read offset, write offset.
    META_FMT = "<HHHH"
    META_STRUCT_CAP     = const(0)
    META_STRUCT_CNT     = const(1)
    META_STRUCT_R_OFF   = const(2)
    META_STRUCT_W_OFF   = const(3)

    def __init__(self, file, data_fmt, capacity):
        self.Queue = StructFile.StructFile(file, data_fmt, NvQueue.META_FMT)

        meta = self.Queue.ReadMeta()
        print(meta)
        # If no metadata is present in the queue file, reset the metadata and write
        # it to the file.
        if meta is None:
            print("No metadata present, initializing queue.")
            self.Capacity = capacity
            self._MetaReset()
            self._MetaUpdate()
        else:
            print("Existing metadata found.")
            self.Capacity = meta[NvQueue.META_STRUCT_CAP]
            self.Count = meta[NvQueue.META_STRUCT_CNT]
            self.ReadOffset = meta[NvQueue.META_STRUCT_R_OFF]
            self.WriteOffset = meta[NvQueue.META_STRUCT_W_OFF]

            # If the read capacity differs from the capacity argument, update it.
            if self.Capacity is not capacity:
                print("Capacity changed, updating metadata.")
                self.Capacity = capacity
                self._MetaUpdate()

    def __iter__(self):
        print("Creating iter")
        return NvQueueIterator(self)

    def Push(self, *item):
        if self.Space() is 0:
            return -1
        print("[NvQueue] Writing tuple to file: {}".format(item))
        self.Queue.WriteData(self.WriteOffset, *item)
        self.WriteOffset = self._OffsetAdvance(self.WriteOffset)
        self._CountInc()
        self._MetaUpdate()
        return self.Count

    def Pop(self):
        if self.Count is 0:
            return None

        data = self.Queue.ReadData(self.ReadOffset)
        self.ReadOffset = self._OffsetAdvance(self.ReadOffset)
        self._CountDec()
        self._MetaUpdate()
        return data

    def Space(self):
        return self.Capacity - self.Count

    def Clear(self):
        self.Queue.Clear()
        self._MetaReset()
        self._MetaUpdate()

    def Delete(self):
        self.Queue.Delete()

    def _MetaReset(self):
        self.ReadOffset = 0
        self.WriteOffset = 0
        self.Count = 0

    def _MetaUpdate(self):
        self.Queue.WriteMeta(self.Capacity, self.Count,
                             self.ReadOffset, self.WriteOffset)

    def _OffsetAdvance(self, offset):
        offset = offset + 1
        if offset >= self.Capacity:
            offset = 0
        return offset

    def _CountInc(self):
        self.Count = self.Count + 1

    def _CountDec(self):
        self.Count = self.Count - 1
