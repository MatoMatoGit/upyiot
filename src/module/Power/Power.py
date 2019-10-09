try:
    import machine
    from machine import Pin
    print("Machine")
except:
    from stubs.PinStub import Pin
    from stubs import machine
    
import uerrno as errno
from micropython import const
from drivers.Battery import Battery
from middleware.StructFile import StructFile
from middleware.SubjectObserver.SubjectObserver import Subject
from middleware.Singleton import Singleton

SLEEP_TIME_MAX_SEC = const(86400)

class PowerSupply(object):
    
    EN_POLARITY_ACTIVE_LOW   = const(0)
    EN_POLARITY_ACTIVE_HIGH  = const(1)
    
    def __init__(self, en_pin_nr, en_polarity, voltage):
        self.Voltage = voltage
        self.PinEnable = Pin(en_pin_nr, Pin.OUT)
        self.Enabled = False
        self.Polarity = en_polarity
        self.Enable(False)

    def Enable(self, en):
        if self.Enabled is True:
            return
        self.Enabled = en       
        if self.Polarity is PowerSupply.EN_POLARITY_ACTIVE_LOW:
            en = not en
        en = int(en)
        self.PinEnable.set(en)


class ServicePowerManager(object):
    
    def __init__(self, sleep_time_sec=SLEEP_TIME_MAX_SEC, 
                voltage=None, supply_obj=None):
        self.Supply = supply_obj
        self.Voltage = voltage
        self.SleepTime = sleep_time_sec
        self.RemainingTime = self.SleepTime
        self.Asleep = False
           
    def Suspend(self):
        if self.RemainingTime <= self.SleepTime:
            self.RemainingTime = self.SleepTime
        
        self.Asleep = True

    def RemainingTimeSet(self, remaining_time_sec):
        self.RemainingTime = remaining_time_sec
        
    def _AsleepReset(self):
        self.Asleep = False


class PowerManager:
    
    SERVICE_INTERVAL_SEC    = const(10)
    BATTERY_LOW_SLEEP_SEC   = const(3600)
    SLEEP_DATA_FMT          = "<II"
    SLEEP_FILE_NAME         = "/sleep"

    def __init__(self, directory, battery, battery_level_threshold, min_sleep_duration_sec):

        # Create a set for all BeforeSleep callbacks.
        self.CbsBeforeSleep = set()
        # Create a set for all LowBattery callbacks.
        self.CbsLowBattery = set()
        # Create a lsit for all ServicePowerManager objects.
        self.ServicePowerManagers = []
        # Create a set for all PowerSupply objects.
        self.PowerSupplies = set()

        self.Battery = battery
        self.BatteryLevel = Subject()
        self.BatteryLevelThreshold = battery_level_threshold
        self.MinSleepDuration = min_sleep_duration_sec
        self.SleepData = StructFile.StructFile(directory + PowerManager.SLEEP_FILE_NAME,
                                               PowerManager.SLEEP_DATA_FMT)

        self.ServiceInit = False

    def WokeFromSleep(self):
        # Check the reset cause to determine if the device was
        # woken from sleep.
        return machine.reset_cause() is machine.DEEPSLEEP_RESET
    
    def RegisterCallbackBeforeSleep(self, callback):
        self.CbsBeforeSleep.add(callback)
        
    def RegisterCallbackLowBattery(self, callback):
        self.CbsLowBattery.add(callback)
             
    def RegisterServicePowerManager(self, svc_power_mngr_obj):
        # Check if the service power manager has a required voltage which has not been
        # linked to a supply yet.
        if svc_power_mngr_obj.Supply is None and svc_power_mngr_obj.Voltage is not None:
            print(svc_power_mngr_obj.Voltage)
            # Get a supply from the required voltage.
            svc_power_mngr_obj.Supply = self._SupplyFromVoltageReq(svc_power_mngr_obj.Voltage)
            # No supply found.
            if svc_power_mngr_obj.Supply is None:
                return errno.EEXIST
        # Add the service power manager.
        self.ServicePowerManagers.append(svc_power_mngr_obj)
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
            print(cb)
            cb()
   
    def _Sleep(self, seconds):
        # Notify all registered callbacks
        self._NotifyBeforeSleep()
        machine.deepsleep(seconds)   
                 
    def _SleepForever(self):
        # Notify all registered callbacks
        self._NotifyBeforeSleep()
        machine.deepsleep()
        
    def _SupplyFromVoltageReq(self, voltage):
        print("Finding supply for voltage req: {}".format(voltage))
        for supply in self.PowerSupplies:
            print(supply.Voltage)
            if supply.Voltage == voltage:
                print("Found suitable supply")
                return supply
        print("No supply found")
        return None

    def Service(self):
        if self.ServiceInit is False:
            print("Initializing Service")

            print("Entries in sleep file: {}".format(self.SleepData.Count))
            # Load previous sleep time
            if self.SleepData.Count > 0:
                sleep_duration = self.SleepData.ReadData(self.SleepData.Count - 1)[0]
                print("Woke up from %d second sleep." % sleep_duration)

            # Loop through the sleep data in the sleep file
            # and calculate (and set) the remaining time.
            for i in range(0, self.SleepData.Count - 1):
                print("Reading sleep file entry: {}".format(i))
                sleep_data = self.SleepData.ReadData(i)
                rem_time = sleep_data[0] - sleep_duration
                if rem_time <= 0:
                    rem_time = self.ServicePowerManagers[i].SleepTime
                print("Remaining time: {}".format(rem_time))
                self.ServicePowerManagers[i].RemainingTimeSet(rem_time)
            self.ServiceInit = True
            print("Initialized")

        # Read the battery level.
        self.BatteryLevel.State = self.Battery.LevelRead()
        # Check if the current battery level is below the threshold.
        # If this is the case the device will go to sleep even when not
        # requested.
        if self.BatteryLevel.State <= self.BatteryLevelThreshold:
            print("Battery level below threshold")
            self._NotifyLowBattery()
            self._Sleep(PowerManager.BATTERY_LOW_SLEEP_SEC * 1000)

        if self.SleepData.Count > 0:
            print("Clearing sleep data file")
            # Clear the sleep file to store new sleep data.
            self.SleepData.Clear()

        # Set variables used in the scheduling loop.
        if len(self.ServicePowerManagers) > 0:
            goto_sleep = True
        else:
            goto_sleep = False
        sleep_duration = SLEEP_TIME_MAX_SEC

        # Loop through the set of coro power managers and check if each of them
        # is ready to sleep.
        for svc_pwr_mngr in self.ServicePowerManagers:
            if svc_pwr_mngr.Asleep is True:
                print("{} is alseep".format(svc_pwr_mngr))
                # Get the remaining sleep time for the manager and append it
                # to the sleep data file.
                rem_time = svc_pwr_mngr.RemainingTime
                self.SleepData.AppendData(rem_time, 0)
                print("Remaining time: {} sec".format(rem_time))

                # Check if the remaining time is greater than the minimal sleep
                # time.
                if rem_time >= self.MinSleepDuration:
                    print("Remaining time qualifies for a sleep request")
                    # Save the remaining time for this manager if it is the smallest amount
                    # of time of all ServicePowerManagers.
                    if rem_time < sleep_duration:
                        sleep_duration = rem_time
                        print("New sleep duration: {} sec".format(sleep_duration))

                # If the task has a small amount of sleep time left to sleep, let the
                # task run until the next cycle when a larger amount is remaining.
                else:
                    print("Resetting sleep state")
                    svc_pwr_mngr.AsleepReset()
                    goto_sleep = False
                    break
            else:
                print("{} is NOT alseep".format(svc_pwr_mngr))
                goto_sleep = False
                break

        # If all services indicate to go to sleep.
        if goto_sleep is True:
            # Append the actual sleep duration as last entry and
            # go to sleep.
            self.SleepData.AppendData(sleep_duration, 0)
            self._Sleep(sleep_duration)

        print("Exiting Service")
