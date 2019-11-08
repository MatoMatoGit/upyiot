import sys
sys.path.append('../')

# Test libraries
import unittest
from TestUtil import TestUtil
from stubs.TestObserver import TestObserver
from stubs.TestBattery import TestBattery
from stubs import machine

# Unit Under Test
from upyiot.module.Power.Power import PowerManager
from upyiot.module.Power.Power import PowerSupply
from upyiot.module.Power.Power import ServicePowerManager

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


class test_ServicePowerManager(unittest.TestCase):

    SLEEP_TIME = 1000
    VOLTAGE = 3.3

    SvcPwrMngr = None

    def setUp(arg):
        test_ServicePowerManager.SvcPwrMngr = ServicePowerManager(test_ServicePowerManager.SLEEP_TIME,
                                                                  test_ServicePowerManager.VOLTAGE)

    def tearDown(arg):
        return

    def test_Constructor(self):
        self.assertEqual(self.SvcPwrMngr.Voltage, test_ServicePowerManager.VOLTAGE)
        self.assertEqual(self.SvcPwrMngr.RemainingTime, test_ServicePowerManager.SLEEP_TIME)

    def test_Suspend(self):
        return


class test_PowerManager(unittest.TestCase):

    POWER_MNGR_DIR = "./"
    BAT_LOW_THRESHOLD = 25
    MIN_SLEEP_DURATION = 5
    Battery = None
    PwrMngr = None

    CallCountBeforeSleep = 0
    CallCountLowBattery = 0

    @staticmethod
    def PowerMngrCallbackBeforeSleep():
        test_PowerManager.CallCountBeforeSleep = test_PowerManager.CallCountBeforeSleep + 1
        print("Power Manager callback: Before sleep")

    @staticmethod
    def PowerMngrCallbackLowBattery():
        test_PowerManager.CallCountLowBattery = test_PowerManager.CallCountLowBattery + 1
        print("Power Manager callback: Low battery")

    def setUp(arg):
        machine.wake_up()
        test_PowerManager.Battery = TestBattery()
        test_PowerManager.PwrMngr = PowerManager(test_PowerManager.POWER_MNGR_DIR,
                                                 test_PowerManager.Battery,
                                                 test_PowerManager.BAT_LOW_THRESHOLD,
                                                 test_PowerManager.MIN_SLEEP_DURATION)
        return

    def tearDown(arg):
        test_PowerManager.PwrMngr.SleepData.Delete()
        test_PowerManager.CallCountLowBattery = 0
        test_PowerManager.CallCountBeforeSleep = 0
        return

    def test_Constructor(self):
        self.assertIsNotNone(self.PwrMngr)

        file_exists = TestUtil.FileExists(test_PowerManager.POWER_MNGR_DIR +
                                          PowerManager.SLEEP_FILE_NAME)
        self.assertTrue(file_exists)

    def test_WokeFromSleep(self):
        woke_from_sleep = self.PwrMngr.WokeFromSleep()
        self.assertTrue(woke_from_sleep)

    def test_RegisterCallbackBeforeSleep(self):
        self.PwrMngr.RegisterCallbackBeforeSleep(
            test_PowerManager.PowerMngrCallbackBeforeSleep)

        self.assertEqual(len(self.PwrMngr.CbsBeforeSleep), 1)

    def test_RegisterCallbackLowBattery(self):
        self.PwrMngr.RegisterCallbackLowBattery(
            test_PowerManager.PowerMngrCallbackLowBattery)

        self.assertEqual(len(self.PwrMngr.CbsLowBattery), 1)

    def test_ObserverAttachBatteryLevel(self):
        battery_lvl_observer = TestObserver()

        self.PwrMngr.ObserverAttachBatteryLevel(battery_lvl_observer)
        self.assertEqual(self.PwrMngr.BatteryLevel.ObserverCount, 1)

    def test_RegisterPowerSupply(self):
        supply = 1

        self.PwrMngr.RegisterPowerSupply(supply)

        self.assertEqual(len(self.PwrMngr.PowerSupplies), 1)

    def test_RegisterServicePowerManagerVoltageRequirement(self):
        supply = PowerSupply(1, PowerSupply.EN_POLARITY_ACTIVE_LOW, 3.3)
        self.PwrMngr.RegisterPowerSupply(supply)

        svc_pwr_mngr = ServicePowerManager(voltage=3.3)

        res = self.PwrMngr.RegisterServicePowerManager(svc_pwr_mngr)

        self.assertEqual(res, 0)
        self.assertEqual(len(self.PwrMngr.ServicePowerManagers), 1)
        self.assertEqual(svc_pwr_mngr.Supply, supply)

    def test_ServiceInitNoSleepData(self):
        self.assertFalse(self.PwrMngr.ServiceInit)

        self.PwrMngr.Service()
        self.assertTrue(self.PwrMngr.ServiceInit)

    def test_ServiceInitWithSleepDurationAndServicePowerManagerEntries(self):
        rem_time_0 = 11
        rem_time_1 = 18
        sleep_time = 5

        self.PwrMngr.SleepData.AppendData(rem_time_0, 0)
        self.PwrMngr.SleepData.AppendData(rem_time_1, 0)
        self.PwrMngr.SleepData.AppendData(sleep_time, 0)

        svc_pwr_mngr_0 = ServicePowerManager()
        self.PwrMngr.RegisterServicePowerManager(svc_pwr_mngr_0)

        svc_pwr_mngr_1 = ServicePowerManager()
        self.PwrMngr.RegisterServicePowerManager(svc_pwr_mngr_1)

        self.PwrMngr.Service()

        self.assertEqual(self.PwrMngr.SleepData.Count, 0)

        self.assertEqual(svc_pwr_mngr_0.RemainingTime, rem_time_0 - sleep_time)
        self.assertEqual(svc_pwr_mngr_1.RemainingTime, rem_time_1 - sleep_time)

    def test_ServiceInitServicePowerManagerNoRemainingTime(self):
        rem_time = 0
        sleep_time = 5

        self.PwrMngr.SleepData.AppendData(rem_time, 0)
        self.PwrMngr.SleepData.AppendData(sleep_time, 0)

        svc_pwr_mngr = ServicePowerManager()
        self.PwrMngr.RegisterServicePowerManager(svc_pwr_mngr)

        self.PwrMngr.Service()

        self.assertEqual(svc_pwr_mngr.RemainingTime, svc_pwr_mngr.SleepTime)

    def test_ServiceReadBatteryLevelWithObserver(self):
        bat_lvl = 50
        bat_lvl_observer = TestObserver()

        self.PwrMngr.ObserverAttachBatteryLevel(bat_lvl_observer)
        self.Battery.LevelSet(bat_lvl)

        self.PwrMngr.Service()

        self.assertEqual(self.PwrMngr.BatteryLevel.State, bat_lvl)
        self.assertEqual(bat_lvl_observer.State, bat_lvl)

    def test_ServiceGotoSleepFromBatteryBelowThresholdWithCallbacks(self):
        bat_lvl = test_PowerManager.BAT_LOW_THRESHOLD

        self.Battery.LevelSet(bat_lvl)
        self.PwrMngr.RegisterCallbackLowBattery(
            test_PowerManager.PowerMngrCallbackLowBattery)
        self.PwrMngr.RegisterCallbackBeforeSleep(
            test_PowerManager.PowerMngrCallbackBeforeSleep)

        self.PwrMngr.Service()

        self.assertEqual(self.CallCountLowBattery, 1)
        self.assertEqual(self.CallCountBeforeSleep, 1)

        self.assertTrue(machine.is_asleep())

    def test_ServiceGotoSleepFromServicePowerManagerSuspend(self):
        rem_time = 15
        sleep_time = 10

        self.PwrMngr.SleepData.AppendData(rem_time, 0)
        self.PwrMngr.SleepData.AppendData(sleep_time, 0)

        svc_pwr_mngr = ServicePowerManager()
        self.PwrMngr.RegisterServicePowerManager(svc_pwr_mngr)

        svc_pwr_mngr.Suspend()

        self.PwrMngr.Service()

        self.assertTrue(machine.is_asleep())
        self.assertEqual(machine.asleep_for(), rem_time - sleep_time)

    def test_ServiceGotoSleepFromShortestServicePowerManagerSuspend(self):
        rem_time_0 = 18
        rem_time_1 = 15
        sleep_time = 5

        self.PwrMngr.SleepData.AppendData(rem_time_0, 0)
        self.PwrMngr.SleepData.AppendData(rem_time_1, 0)
        self.PwrMngr.SleepData.AppendData(sleep_time, 0)

        svc_pwr_mngr_0 = ServicePowerManager()
        self.PwrMngr.RegisterServicePowerManager(svc_pwr_mngr_0)

        svc_pwr_mngr_1 = ServicePowerManager()
        self.PwrMngr.RegisterServicePowerManager(svc_pwr_mngr_1)

        svc_pwr_mngr_0.Suspend()
        svc_pwr_mngr_1.Suspend()

        self.PwrMngr.Service()

        self.assertTrue(machine.is_asleep())
        self.assertEqual(machine.asleep_for(), rem_time_1 - sleep_time)

    def test_ServiceCancelSleepFromServicePowerManagerNotAsleep(self):
        rem_time_0 = 18
        rem_time_1 = 15
        sleep_time = 5

        self.PwrMngr.SleepData.AppendData(rem_time_0, 0)
        self.PwrMngr.SleepData.AppendData(rem_time_1, 0)
        self.PwrMngr.SleepData.AppendData(sleep_time, 0)

        svc_pwr_mngr_0 = ServicePowerManager()
        self.PwrMngr.RegisterServicePowerManager(svc_pwr_mngr_0)

        svc_pwr_mngr_1 = ServicePowerManager()
        self.PwrMngr.RegisterServicePowerManager(svc_pwr_mngr_1)

        svc_pwr_mngr_0.Suspend()

        self.PwrMngr.Service()

        self.assertFalse(machine.is_asleep())

    def test_ServiceResetAsleepServicePowerManagerLowerThanMinSleepDuration(self):
        rem_time_0 = 18
        rem_time_1 = 4
        sleep_time = 5

        self.PwrMngr.SleepData.AppendData(rem_time_0, 0)
        self.PwrMngr.SleepData.AppendData(rem_time_1, 0)
        self.PwrMngr.SleepData.AppendData(sleep_time, 0)

        svc_pwr_mngr_0 = ServicePowerManager()
        self.PwrMngr.RegisterServicePowerManager(svc_pwr_mngr_0)

        svc_pwr_mngr_1 = ServicePowerManager()
        self.PwrMngr.RegisterServicePowerManager(svc_pwr_mngr_1)

        svc_pwr_mngr_0.Suspend()

        self.PwrMngr.Service()

        self.assertFalse(machine.is_asleep())

        self.assertEqual(svc_pwr_mngr_1.RemainingTime, svc_pwr_mngr_1.SleepTime)

