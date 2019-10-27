import sys
sys.path.append('../upyiot/')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from middleware.NvQueue import NvQueue

# Other
import uos as os


class test_NvQueue(unittest.TestCase):

    DATA_FMT = "<HH"
    FILE = "./tmp"
    CAPACITY = 4
    Queue = None

    def setUp(arg):
        test_NvQueue.Queue = NvQueue.NvQueue(test_NvQueue.FILE, test_NvQueue.DATA_FMT, test_NvQueue.CAPACITY)
        return

    def tearDown(arg):
        os.remove(test_NvQueue.FILE)
        return

    def test_Constructor(self):
        file_exists = TestUtil.FileExists(test_NvQueue.FILE)
        self.assertTrue(file_exists)
        self.assertEqual(self.Queue.Capacity, test_NvQueue.CAPACITY)
        self.assertEqual(self.Queue.Count, 0)
        self.assertEqual(self.Queue.ReadOffset, 0)
        self.assertEqual(self.Queue.WriteOffset, 0)

    def test_PushOne(self):
        w_data = (1, 2)

        count = self.Queue.Push(*w_data)

        self.assertEqual(count, 1)
        self.assertNotEqual(self.Queue.WriteOffset, 0)

    def test_PushMaxPlusOne(self):
        w_data = (1, 2)

        for i in range(0, self.Queue.Capacity):
            count = self.Queue.Push(*w_data)
            self.assertEqual(count, i + 1)

        self.assertEqual(self.Queue.Push(*w_data), -1)

    def test_PopOne(self):
        w_data = (1, 2)

        self.Queue.Push(*w_data)
        r_data = self.Queue.Pop()

        self.assertEqual(r_data, w_data)
        self.assertEqual(self.Queue.Count, 0)
        self.assertEqual(self.Queue.ReadOffset, self.Queue.WriteOffset)

    def test_Space(self):
        w_data = (1, 2)

        self.Queue.Push(*w_data)
        self.Queue.Push(*w_data)

        self.assertEqual(self.Queue.Space(), self.Queue.Capacity - 2)

        self.Queue.Pop()

        self.assertEqual(self.Queue.Space(), self.Queue.Capacity - 1)

    def test_PopMaxPlusOne(self):

        for i in range(0, self.Queue.Capacity):
            w_data = (i, i + 1)
            print(w_data)
            count = self.Queue.Push(*w_data)
            self.assertEqual(count, i + 1)

        for i in range(0, self.Queue.Capacity):
            r_data = self.Queue.Pop()
            print(r_data)
            w_data = (i, i + 1)
            self.assertEqual(r_data, w_data)
            self.assertEqual(self.Queue.Count, self.Queue.Capacity - (i + 1))

        self.assertEqual(self.Queue.Pop(), None)

    def test_Clear(self):
        w_data = (1, 2)

        self.Queue.Push(*w_data)
        self.Queue.Clear()
        self.assertEqual(self.Queue.Count, 0)

        queue = NvQueue.NvQueue(test_NvQueue.FILE, test_NvQueue.DATA_FMT, test_NvQueue.CAPACITY)
        self.assertEqual(queue.Count, 0)
        self.assertEqual(queue.ReadOffset, 0)
        self.assertEqual(queue.WriteOffset, 0)

    def test_ReloadExistingAtConstruction(self):
        w_data = (1, 2)
        self.Queue.Push(*w_data)
        self.Queue.Push(*w_data)
        self.Queue.Pop()
        w_offset = self.Queue.WriteOffset
        r_offset = self.Queue.ReadOffset

        queue = NvQueue.NvQueue(test_NvQueue.FILE, test_NvQueue.DATA_FMT, test_NvQueue.CAPACITY)

        self.assertEqual(queue.Count, 1)
        self.assertEqual(queue.WriteOffset, w_offset)
        self.assertEqual(queue.ReadOffset, r_offset)

    def test_ReloadExistingAtConstructionCapacityChanged(self):
        w_data = (1, 2)
        self.Queue.Push(*w_data)
        w_offset = self.Queue.WriteOffset

        queue = NvQueue.NvQueue(test_NvQueue.FILE, test_NvQueue.DATA_FMT, test_NvQueue.CAPACITY + 1)

        self.assertEqual(queue.Count, 1)
        self.assertEqual(queue.WriteOffset, w_offset)
        self.assertEqual(queue.Capacity, test_NvQueue.CAPACITY + 1)

    def test_Iterator(self):

        for i in range(0, self.Queue.Capacity - 1):
            w_data = (i, i + 1)
            print(w_data)
            count = self.Queue.Push(*w_data)
            self.assertEqual(count, i + 1)

        i = 0
        for item in self.Queue:
            w_data = (i, i + 1)
            self.assertEqual(item, w_data)
            print(item)
            i = i + 1

        self.assertEqual(i, self.Queue.Capacity - 1)

