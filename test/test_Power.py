import sys

sys.path.append('../src/')

import unittest
from module.Power.Power import PowerManager 

class test_Power(unittest.TestCase):

	POWER_MNGR_DIR = "./"
	
	PwrMngr = None
	
	def setUp(arg):
		battery = None
		test_Power.PwrMngr = PowerManager(test_Power.POWER_MNGR_DIR, battery, 25, 10)
		
	def tearDown(arg):
		test_Power.PwrMngr.SleepFile.Delete()
		return

	def test_Constructor(self):
		self.assertIsNotNone(self.PwrMngr)
