import sys

sys.path.append('../src/')

import unittest
from module.SystemTime import SystemTime

class test_SystemTime(unittest.TestCase):

	
	def setUp(arg):
		return
		
	def tearDown(arg):
		return

	def test_Constructor(self):
		sys_time = SystemTime.InstanceAcquire()
		
		self.assertFalse(sys_time is None)
	
	def test_Singleton(self):
		sys_time = SystemTime.InstanceAcquire()
		sys_time1 = SystemTime.InstanceAcquire()

		self.assertEqual(sys_time, sys_time1)
		
		except_occurred = False
		try:
			SystemTime.SystemTime()
		except:
			except_occurred = True
		finally:
			self.assertTrue(except_occurred)

	def test_Service(self):
		SystemTime.Service()
	
	def test_testNow(self):
		sys_time = SystemTime.InstanceAcquire()
		
		SystemTime.Service()
		now = sys_time.Now()
		
		self.assertFalse(now[0] is 0)
		
	def test_NowFormatted(self):
		sys_time = SystemTime.InstanceAcquire()
		
		SystemTime.Service()
		now = sys_time.NowFormatted()
		print("Formatted time: {}".format(now))
		
		self.assertIn('2019', now)
		self.assertIn('T', now)