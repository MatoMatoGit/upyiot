from micropython import const
from SubjectObserver import Subject
import uasyncio


class Battery(object):
    
    BATTERY_READ_INTERVAL_SEC = const(3600)
    LIPO_VOLT_TO_PERCENT_CURVE = (4.4, 3.9, 3.75, 3.7, 3,65, 3)
    LIPO_VOLT_TO_PERCENT_STEP = const(25)
    
    def __init__(self, num_cells, volt_sensor_obj):
        self.NumCells = num_cells
        self.VoltSensor = volt_sensor_obj
        self.Level = Subject()
        
    def Level(self):
        return self.Level.State
    
    def ObserverAttachLevel(self, observer):
        self.Level.Attach(observer)
    
    @staticmethod
    async def Service():
        # Read the current battery voltage, convert it to a percentage,
        # and notify all observers.
        volt = Battery.VoltSensor.Read()
        Battery.Level.State = Battery.VoltageToPercent(volt)
        await uasyncio.sleep(Battery.BATTERY_READ_INTERVAL_SEC)
        
        
    @staticmethod
    def VoltageToPercent(volt):
        if volt > Battery.LIPO_VOLT_TO_PERCENT_CURVE[0]:
            return 100
        i = 0
        # Loop through the battery curve until the measured voltage
        # is higher than the curve value.
        for v in Battery.LIPO_VOLT_TO_PERCENT_CURVE:
            if volt > v:
                break;
            i = i + 1
        # The drained percentage is equal to the number of steps - 1 (if 1
        # step is taken the battery is considered to be full) times
        # the percentage per step.
        return 100 - ((i - 1) * Battery.LIPO_VOLT_TO_PERCENT_STEP)