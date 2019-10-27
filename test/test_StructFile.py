import sys
sys.path.append('../upyiot/')

# Test libraries
import unittest
from TestUtil import TestUtil

# Unit Under Test
from middleware.StructFile import StructFile

# Other
import uos as os
import ustruct


class test_StructFile(unittest.TestCase):
    TEST_FMT = "<HH"
    TEST_FILE = "./tmp"

    Sf = None

    def setUp(arg):
        test_StructFile.Sf = StructFile.StructFile(test_StructFile.TEST_FILE, test_StructFile.TEST_FMT)

    def tearDown(arg):
        try:
            os.remove(test_StructFile.TEST_FILE)
        except OSError as f_err:
            print(f_err)

    def test_Constructor(self):
        self.assertEqual(self.Sf.DataSize, ustruct.calcsize(test_StructFile.TEST_FMT))
        file_exists = TestUtil.FileExists(test_StructFile.TEST_FILE)
        self.assertTrue(file_exists)

    def test_ConstructorWithUserMeta(self):
        user_meta_fmt = "<II"
        os.remove(test_StructFile.TEST_FILE)
        sf = StructFile.StructFile(test_StructFile.TEST_FILE, test_StructFile.TEST_FMT, user_meta_fmt)
        self.assertEqual(sf.DataSize, ustruct.calcsize(test_StructFile.TEST_FMT))
        file_exists = TestUtil.FileExists(test_StructFile.TEST_FILE)
        self.assertTrue(file_exists)

    def test_WriteData(self):
        w_data = (1, 2)
        self.assertEqual(self.Sf.WriteData(0, *w_data), 0)

    def test_ReloadExistingFileAtConstruction(self):
        w_data = (1, 2)
        self.Sf.WriteData(0, *w_data)
        sf_copy = StructFile.StructFile(test_StructFile.TEST_FILE, test_StructFile.TEST_FMT)

    def test_WriteStruct(self):
        struct = ustruct.pack(test_StructFile.TEST_FMT, 1, 2)
        self.assertEqual(self.Sf.WriteStruct(0, struct), 0)

    def test_WriteStructSizeMismatch(self):
        struct = ustruct.pack(test_StructFile.TEST_FMT + 'H', 1, 2, 3)
        self.assertEqual(self.Sf.WriteStruct(0, struct), -1)

    def test_ReadData(self):
        w_data = (1, 2)
        self.Sf.WriteData(0, *w_data)
        r_data = self.Sf.ReadData(0)
        self.assertTrue(r_data == w_data)

    def test_ReadStruct(self):
        w_data = (1, 2)
        self.Sf.WriteData(0, *w_data)
        struct = self.Sf.ReadStruct(0)
        r_data = ustruct.unpack(test_StructFile.TEST_FMT, struct)
        self.assertTrue(r_data == w_data)

    def test_ReadDataNotAvailable(self):
        self.assertEqual(self.Sf.ReadData(0), None)

    def test_WriteReadMeta(self):
        user_meta_fmt = "<HH"
        os.remove(test_StructFile.TEST_FILE)
        sf = StructFile.StructFile(test_StructFile.TEST_FILE, test_StructFile.TEST_FMT, user_meta_fmt)
        w_meta = (3, 4)

        sf.WriteMeta(*w_meta)
        r_meta = sf.ReadMeta()

        self.assertEqual(r_meta, w_meta)

    def test_ReadMetaNotAvailable(self):
        user_meta_fmt = "<HH"
        os.remove(test_StructFile.TEST_FILE)
        sf = StructFile.StructFile(test_StructFile.TEST_FILE, test_StructFile.TEST_FMT, user_meta_fmt)
        self.assertEqual(sf.ReadMeta(), None)

    def test_WriteReadMetaWriteReadData(self):
        user_meta_fmt = "<HH"
        os.remove(test_StructFile.TEST_FILE)
        sf = StructFile.StructFile(test_StructFile.TEST_FILE, test_StructFile.TEST_FMT, user_meta_fmt)
        w_meta = (3, 4)

        sf.WriteMeta(*w_meta)
        r_meta = sf.ReadMeta()

        self.assertEqual(r_meta, w_meta)

        w_data = (1, 2)
        self.Sf.WriteData(0, *w_data)
        r_data = self.Sf.ReadData(0)

        self.assertEqual(r_data, w_data)

    def test_Clear(self):
        self.Sf.WriteData(0, 1, 2)

        self.Sf.Clear()
        self.assertEqual(self.Sf.ReadData(0), None)

    def test_Delete(self):
        self.Sf.Delete()

        file_exists = TestUtil.FileExists(test_StructFile.TEST_FILE)
        self.assertFalse(file_exists)

    def test_IteratorNoMax(self):
        index_start = 0
        index_end = 4
        w_data_set = []
        i = 0
        for i in range(index_start, index_end + 1):
            w_data = (i, i+1)
            w_data_set.append(w_data)
            print(w_data)
            self.Sf.WriteData(i, *w_data)
        print(w_data_set)
        self.Sf.IteratorConfig(index_start, index_end)
        i = 0
        for r_data in self.Sf:
            print(r_data)
            self.assertEqual(r_data, w_data_set[i])
            i = i + 1

        self.assertEqual(len(w_data_set), i)

    def test_IteratorWithMax(self):
        index_start = 3
        index_end = 4
        count = 5
        i = 0
        w_data_set = []
        for i in range(0, 5):
            w_data = (i, i+1)
            w_data_set.append(w_data)
            print(w_data)
            self.Sf.WriteData(i, *w_data)
        print(w_data_set)
        self.Sf.IteratorConfig(index_start, index_end, count)
        i = 0
        for r_data in self.Sf:
            print(r_data)
            idx = self.Sf.IteratorIndex()
            print(idx)
            self.assertTrue(r_data == w_data_set[idx])
            i = i + 1

        self.assertEqual(len(w_data_set), i)

    def test_IteratorNoFile(self):
        self.Sf.Delete()
        i = 0
        for r_data in self.Sf:
            i = i + 1

        self.assertEqual(i, 0)

    def test_IteratorNoIteratorConfig(self):
        i = 0
        for r_data in self.Sf:
            i = i + 1

        self.assertEqual(i, 0)


