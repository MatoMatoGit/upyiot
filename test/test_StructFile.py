import sys
sys.path.append('../src/')

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
		self.assertEqual(self.Sf.Count, 0)
		self.assertEqual(self.Sf.DataSize, ustruct.calcsize(test_StructFile.TEST_FMT))
		file_exists = TestUtil.FileExists(test_StructFile.TEST_FILE)
		self.assertTrue(file_exists)

	def test_AppendData(self):
		self.assertEqual(self.Sf.AppendData(1, 2), 1)
		
	def test_ReloadExistingFileAtConstruction(self):
		self.Sf.AppendData(1, 2)
		sf_copy = StructFile.StructFile(test_StructFile.TEST_FILE, test_StructFile.TEST_FMT)
		self.assertEqual(sf_copy.Count, 1)
	
	def test_AppendStruct(self):
		struct = ustruct.pack(test_StructFile.TEST_FMT, 1, 2)
		self.assertEqual(self.Sf.AppendStruct(struct), 1)

	def test_AppendStructSizeMismatch(self):
		struct = ustruct.pack(test_StructFile.TEST_FMT + 'H', 1, 2, 3)
		self.assertEqual(self.Sf.AppendStruct(struct), -1)
	
	def test_ReadData(self):
		w_data = (1, 2)
		self.Sf.AppendData(*w_data)
		r_data = self.Sf.ReadData(0)
		self.assertTrue(r_data == w_data)
	
	def test_ReadStruct(self):
		w_data = (1, 2)
		self.Sf.AppendData(*w_data)
		struct = self.Sf.ReadStruct(0)
		r_data = ustruct.unpack(test_StructFile.TEST_FMT, struct)
		self.assertTrue(r_data == w_data)
	
	def test_ReadDataNotAvailable(self):
		self.assertEqual(self.Sf.ReadData(0), None)
		
	def test_Clear(self):
		self.Sf.AppendData(1, 2)
		
		self.Sf.Clear()
		
		self.assertEqual(self.Sf.Count, 0)
		self.assertEqual(self.Sf.ReadData(0), None)
	
	def test_Delete(self):
		self.Sf.Delete()
		
		file_exists = TestUtil.FileExists(test_StructFile.TEST_FILE)
		self.assertFalse(file_exists)

	def test_Iterator(self):	
		i = 0
		for i in range(0, 10, 2):
			w_data = (i, i+1)
			print(w_data)
			self.Sf.AppendData(*w_data)

		i = 0
		for r_data in self.Sf:
			print(r_data)
			self.assertTrue(r_data == (i, i+1))
			i = i + 2

		self.assertEqual(self.Sf.Count, i/2)
		
	
	def test_IteratorNoFile(self):
		self.Sf.Delete()
		i = 0
		for r_data in self.Sf:
			i = i + 1
		
		self.assertEqual(i, 0)


