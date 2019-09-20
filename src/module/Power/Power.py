try:
    import machine
    from machine import Pin
    print("Machine")
except:
    from stubs.PinStub import Pin
    from stubs import machine
    
import uerrno as errno
from micropython import const
from drivers import Battery
from middleware.StructFile import StructFile
from middleware.SubjectObserver.SubjectObserver import Subject

SLEEP_TIME_MAX_SEC = const(86400)

class PowerSupply(object):
    
    POWER_SUPPLY_EN_POLARITY_ACTIVE_LOW   = const(0)
    POWER_SUPPLY_EN_POLARITY_ACTIVE_HIGH  = const(1)
    
    def __init__(self, en_pin, en_polarity, voltage):
        self.Voltage = voltage
        self.PinEnable = Pin(en_pin, Pin.OUT)
        self.Enabled = False
        self.Polarity = en_polarity

    def Enable(self, en):
        if self.Enabled is True:
            return
        self.Enabled = en       
        if self.Polarity is PowerSupply.SUPPLY_EN_POLARITY_ACTIVE_LOW:
            en = not en
        en = int(en)
        self.PinEnable.value(en)


class ServicePowerManager(object):
    
    def __init__(self, sleep_time_sec=SLEEP_TIME_MAX_SEC, 
                voltage=None, supply_obj=None):
        self.Supply = supply_obj
        self.Voltage = voltage
        self.SleepTime = sleep_time_sec
        self.RemaningTime = self.SleepTime
        self.Asleep = False
           
    def Suspend(self):
        if self.RemainingTime <= self.SleepTime:
            self.RemainingTime = self.SleepTime
        
        self.Asleep = True

    def _RemainingTimeSet(self, remaining_time_sec):
        self.RemaningTime = remaining_time_sec
        
    def _AsleepReset(self):
        self.Asleep = False


class PowerManager(object):
    
    SERVICE_INTERVAL_SEC    = const(10)
    BATTERY_LOW_SLEEP_SEC   = const(3600)
    SLEEP_DATA_FMT          = "<II"
    SLEEP_FILE_NAME         = "/sleep"
    
    _ServiceInit = False
    
    def __init__(self, directory, battery, battery_level_threshold, min_sleep_duration_sec):
        
        # Create a set for all BeforeSleep callbacks.
        self.CbsBeforeSleep = set()
        # Create a set for all LowBattery callbacks.
        self.CbsLowBattery = set()
        # Create a set for all ServicePowerManager objects.
        self.ServicePowerManagers = set()
        # Create a set for all PowerSupply objects.
        self.PowerSupplies = set()
        
        self.Battery = battery
        self.BatteryLevel = Subject()
        self.BatteryLevelThreshold = battery_level_threshold
        self.MinSleepDuration = min_sleep_duration_sec
        self.SleepFile = StructFile.StructFile(directory + PowerManager.SLEEP_FILE_NAME, 
                                               PowerManager.SLEEP_DATA_FMT)
        # Load previous sleep time
        if self.SleepFile.Count > 0:
            self.SleepDuration = StructFile.ReadData(self.SleepFile.Count)[0]

    def WokeFromSleep(self):
        # Check the reset cause to determine if the device was
        # woken from sleep.
        return machine.reset_cause() is machine.DEEPSLEEP_RESET
    
    def RegisterCallbackBeforeSleep(self, callback):
        self.CbsBeforeSleep.add(callback)
        
    def RegisterCalllbackLowBattery(self, callback):
        self.CbsLowBattery.add(callback)
             
    def RegisterServicePowerManager(self, svc_power_mngr_obj):
        # Check if the service power manager has a required voltage which has not been
        # linked to a supply yet.
        if svc_power_mngr_obj.Supply is None and svc_power_mngr_obj.Voltage is not None:
            # Get a supply from the required voltage.
            self._SupplyFromVoltageReq(svc_power_mngr_obj.Voltage)
            # No supply found.
            if svc_power_mngr_obj.Supply is None:
                return errno.EEXIST
        # Add the service power manager.
        self.ServicePowerManagers.add(svc_power_mngr_obj)
        return 0
        
    def RegisterPowerSupply(self, power_supply_obj):
        self.PowerSupplies.add(power_supply_obj)    
           
    def ObserverAttachBatteryLevel(self, observer):
        self.BatteryLevel.Attach(observer)            

    def _NotifyBeforeSleep(self):
        for cb in self.CbsBeforeSleep:
            cb()
            
    def _NotifyLowBattery(self):
        for cb in self.CbsLowBattery:
            cb()
   
    def _Sleep(self, seconds):
        # Notify all registered callbacks
        PowerManager._NotifyBeforeSleep()
        machine.deepsleep(seconds)   
                 
    def _SleepForever(self):
        # Notify all registered callbacks
        self._NotifyBeforeSleep()
        machine.deepsleep()
        
    def _SupplyFromVoltageReq(self, voltage):
        for supply in self.PowerSupplies:
            if supply.Voltage is voltage:
                return PowerSupply
        
        return None
                

def Service():
    if PowerManager._ServiceInit is False:
        rem_time = 0
        i = 0
        # Loop through the sleep data in the sleep file
        # and calculate (and set) the remaining time.
        for sleep_data in PowerManager.SleepFile:
            try:
                rem_time = sleep_data[0] - PowerManager.SleepDuration
                if rem_time <= 0:
                    rem_time = PowerManager.ServicePowerManagers[i].SleepTime
                PowerManager.ServicePowerManagers[i]._RemainingTimeSet(rem_time)
            except:
                print("Error setting remaining sleep time.")
            i = i + 1
        PowerManager._ServiceInit = True
    
    # Read the battery level.
    PowerManager.BatteryLevel = PowerManager.Battery.ReadLevel()
    
    # Check if the current battery level is below the threshold.
    # If this is the case the device will go to sleep even when not 
    # requested.
    if PowerManager.BatterLevel < PowerManager.BatteryLevelThreshold:
        PowerManager._NotifyLowBattery()
        PowerManager._Sleep(PowerManager.BATTERY_LOW_SLEEP_SEC * 1000)
    
    # Clear the sleep file to store new sleep data.
    PowerManager.SleepFile.Clear()
    
    # Set variables used in the scheduling loop.
    goto_sleep = True
    PowerManager.SleepDuration = SLEEP_TIME_MAX_SEC
    rem_time = 0
    
    # Loop through the set of coro power managers and check if each of them
    # is ready to sleep. 
    for sched in PowerManager.ServicePowerManagers:
        if sched.Asleep is True:
            
            # Get the remaining sleep time for the manager and append it
            # to the sleep data file.
            rem_time = sched.RemainingTime
            PowerManager.SleepFile.AppendData(rem_time)
            
            # Check if the remaining time is greater than the minimal sleep
            # time.
            if rem_time >= PowerManager.MinSleepTime:
                # Save the remaining time for this manager if it is the smallest amount
                # of time of all schedulers.                       
                if rem_time < PowerManager.SleepDuration:
                    PowerManager.SleepDuration = rem_time
            
            # If the task has a small amount of sleep time left to sleep, let the
            # task run until the next cycle when a larger amount is remaining.
            else:
                sched.AsleepReset()
        else:
            goto_sleep = False
            break
    
    # If all coros indicate to go to sleep.
    if goto_sleep is True:
        # Append the actual sleep duration as last entry and
        # go to sleep.
        PowerManager.SleepFile.AppendData(PowerManager.SleepDuration)
        PowerManager._Sleep(PowerManager.SleepDuration)

    
        