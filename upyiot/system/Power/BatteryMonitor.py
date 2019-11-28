from upyiot.drivers.Sensors.BatteryLevel import BatteryLevel
from upyiot.middleware.Sensor.Sensor import Sensor
from upyiot.middleware.SubjectObserver.SubjectObserver import Observer


class BatteryMonitor(Observer):

    def __init__(self, directory, battery_level_threshold):
        super().__init__()
        self.BatteryLevel = 100
        self.BatteryLevelSensor = Sensor(directory, 'batlvl', 20, BatteryLevel(1, 1, 1))
        self.BatteryLevelSensor.ObserverAttachNewSample(self)
        self.BatteryLevelThreshold = battery_level_threshold
        # Create a set for all LowBattery callbacks.
        self.CbsLowBattery = set()
        return

    def RegisterCallbackLowBattery(self, callback):
        self.CbsLowBattery.add(callback)

    def Update(self, arg):
        self.BatteryLevel = arg
        if self.BatteryLevel < self.BatteryLevelThreshold:
            self._NotifyLowBattery()

    def _NotifyLowBattery(self):
        for cb in self.CbsLowBattery:
            print(cb)
            cb()
