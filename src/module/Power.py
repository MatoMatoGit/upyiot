from SubjectObserver import Observer
import Battery
import machine


class BatteryObserver(Observer):
    
    def __init__(self):
        self.BatteryLevel = 100
        
    def Update(self, arg):
        self.BatteryLevel = arg


class Power(object):
    
    BATTERY_LOW_SLEEP_SEC = 3600
    
    def __init__(self, battery_level_threshold):   
        # Create a observer for the battery level. 
        self.BatteryObserver = BatteryObserver()
        # Create a set for all BeforeSleep callbacks.
        self.CbsBeforeSleep = set()
        # Create a set for all LowBattery callbacks.
        self.CbsLowBattery = set()
        self.BatteryLevelThreshold = battery_level_threshold
        self.SleepRequest = 0
    
    def BatteryObserver(self):
        return self.BatteryObserver
       
    def WokeFromSleep(self):
        # Check the reset cause to determine if the device was
        # woken from sleep.
        return machine.reset_cause() is machine.DEEPSLEEP_RESET
    
    def RegisterCallbackBeforeSleep(self, callback):
        self.CbsBeforeSleep.add(callback)
        
    def RegisterCalllbackLowBattery(self, callback):
        self.CbsLowBattery.add(callback)
        
    def RequestSleepMsec(self, milliseconds):
        self.SleepRequest = milliseconds
    
    def RequestSleepSec(self, seconds):
        self.SleepRequest = seconds * 1000
         
    @staticmethod  
    def Service():
        # Check if the current battery level is below the threshold.
        # If this is the case the device will go to sleep even when not 
        # requested.
        if Power.BatterObserver.BatterLevel < Power.BatteryLevelThreshold:
            Power.__NotifyLowBattery()
            Power.__Sleep(Power.BATTERY_LOW_SLEEP_SEC * 1000)
            
        # If sleep has been requested, notify all registered callbacks
        # and enter deep-sleep for the requested amount of time.
        if Power.SleepRequest is not 0:
            Power.__Sleep(Power.SleepRequest)

    def __NotifyBeforeSleep(self):
        for cb in self.CbsBeforeSleep:
            cb()
            
    def __NotifyLowBattery(self):
        for cb in self.CbsLowBattery:
            cb()
   
    def __Sleep(self, milliseconds):
        Power.__NotifyBeforeSleep()
        machine.deepsleep(milliseconds)   
                 
    def __SleepForever(self):
        self.__NotifyBeforeSleep()
        machine.deepsleep()