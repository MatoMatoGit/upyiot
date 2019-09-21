import sys
sys.path.append('../src/')

# Test libraries
import unittest
from TestUtil import TestUtil
from stubs.TestObserver import TestObserver

# Unit Under Test
from module.Power.Power import PowerManager
from module.Power.Power import PowerSupply
#from module.Power.Power import ServicePowerManager

# Other 


class test_PowerSupply(unittest.TestCase):
	
	def setUp(arg):
		return
		
		
	def tearDown(arg):
		return
	
	def test_Constructor(self):
		supply = test_PowerSupply.Supply = PowerSupply(1, PowerSupply.EN_POLARITY_ACTIVE_LOW, 3.3)
		self.assertFalse(supply.Enabled)
		self.assertEqual(supply.PinEnable.get(), 1)
		
		supply = test_PowerSupply.Supply = PowerSupply(1, PowerSupply.EN_POLARITY_ACTIVE_HIGH, 3.3)
		self.assertFalse(supply.Enabled)
		self.assertEqual(supply.PinEnable.get(), 0)
		
	def test_EnableActiveLow(self):
		supply = test_PowerSupply.Supply = PowerSupply(1, PowerSupply.EN_POLARITY_ACTIVE_LOW, 3.3)
		supply.Enable(True)
		
		self.assertTrue(supply.Enabled)
		self.assertEqual(supply.PinEnable.get(), 0)
		
	def test_EnableActiveHigh(self):
		supply = test_PowerSupply.Supply = PowerSupply(1, PowerSupply.EN_POLARITY_ACTIVE_HIGH, 3.3)
		supply.Enable(True)
		
		self.assertTrue(supply.Enabled)
		self.assertEqual(supply.PinEnable.get(), 1)
		

class test_PowerManager(unittest.TestCase):

	POWER_MNGR_DIR = "./"
	
	PwrMngr = None
	
	def PowerMngrCallbackBeforeSleep(self):
		print("Power Manager callback: Before sleep")
		
	def PowerMngrCallbackLowBattery(self):
		print("Power Manager callback: Low battery")
		
	def setUp(arg):
		battery = None
		test_PowerManager.PwrMngr = PowerManager(test_PowerManager.POWER_MNGR_DIR, battery, 25, 10)
		
	def tearDown(arg):
		test_PowerManager.PwrMngr.SleepFile.Delete()
		return

	def test_Constructor(self):
		self.assertIsNotNone(self.PwrMngr)
		
		file_exists = TestUtil.FileExists(test_PowerManager.POWER_MNGR_DIR 
										+ PowerManager.SLEEP_FILE_NAME)
		self.assertTrue(file_exists)
		
	def test_WokeFromSleep(self):
		woke_from_sleep = self.PwrMngr.WokeFromSleep()
		self.assertTrue(woke_from_sleep)
		
	def test_RegisterCallbackBeforeSleep(self):
		self.PwrMngr.RegisterCallbackBeforeSleep(test_PowerManager.PowerMngrCallbackBeforeSleep)
		
		self.assertEqual(len(self.PwrMngr.CbsBeforeSleep), 1)
		
	def test_RegisterCallbackLowBattery(self):
		self.PwrMngr.RegisterCallbackLowBattery(test_PowerManager.PowerMngrCallbackLowBattery)
		
		self.assertEqual(len(self.PwrMngr.CbsLowBattery), 1)
		
	def test_ObserverAttachBatteryLevel(self):
		battery_lvl_observer = TestObserver()
		
		self.PwrMngr.ObserverAttachBatteryLevel(battery_lvl_observer)
		self.assertEqual(self.PwrMngr.BatteryLevel.ObserverCount, 1)
		
	def test_RegisterPowerSupply(self):
		supply = 1
		
		self.PwrMngr.RegisterPowerSupply(supply)
		
		self.assertEqual(len(self.PwrMngr.PowerSupplies), 1)
		
	