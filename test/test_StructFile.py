import StructFile
import unittest
import uos as os
import ustruct

class TestStructFile(unittest.TestCase):
	TEST_FMT = "<HH"
	TEST_FILE = "./tmp"
	
	Sf = None
	
	def setUp(arg):
		TestStructFile.Sf = StructFile.StructFile(TestStructFile.TEST_FILE, TestStructFile.TEST_FMT)
		
	def tearDown(arg):
		try:
			os.remove(TestStructFile.TEST_FILE)
		except OSError as f_err:
			print(f_err)

	def testConstructor(self):       
	    self.assertEqual(self.Sf.Count, 0)
	    
	def testAppendData(self):
		self.assertEqual(self.Sf.AppendData(1, 2), 1)
		
	def testReloadExistingFileAtConstruction(self):
		self.Sf.AppendData(1, 2)
		sf_copy = StructFile.StructFile(TestStructFile.TEST_FILE, TestStructFile.TEST_FMT)
		self.assertEqual(sf_copy.Count, 1)
	
	def testAppendStruct(self):
		struct = ustruct.pack(TestStructFile.TEST_FMT, 1, 2)
		self.assertEqual(self.Sf.AppendStruct(struct), 1)

	def testAppendStructSizeMismatch(self):
		struct = ustruct.pack(TestStructFile.TEST_FMT + 'H', 1, 2, 3)
		self.assertEqual(self.Sf.AppendStruct(struct), -1)
	
	def testReadData(self):
		w_data = (1, 2)
		self.Sf.AppendData(*w_data)
		r_data = self.Sf.ReadData(0)
		self.assertTrue(r_data == w_data)
	
	def testReadStruct(self):
		w_data = (1, 2)
		self.Sf.AppendData(*w_data)
		struct = self.Sf.ReadStruct(0)
		r_data = ustruct.unpack(TestStructFile.TEST_FMT, struct)
		self.assertTrue(r_data == w_data)
	
	def testReadDataNotAvailable(self):
		self.assertEqual(self.Sf.ReadData(0), None)
		
	def testClear(self):
		self.Sf.AppendData(1, 2)
		
		self.Sf.Clear()
		
		self.assertEqual(self.Sf.Count, 0)
		self.assertEqual(self.Sf.ReadData(0), None)
	
	def testDelete(self):
		self.Sf.Delete()
		
		f_exists = True
		try:
			f = open(TestStructFile.TEST_FILE)
		except OSError:
			f_exists = False
		
		self.assertFalse(f_exists)

	def testIterator(self):
		values = range(0, 10, 2)
		
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
		
	
	def testIteratorNoFile(self):
		self.Sf.Delete()
		i = 0
		for r_data in self.Sf:
			i = i + 1
		
		self.assertEqual(i, 0)
		
		

if __name__ == '__main__':
    unittest.main()


