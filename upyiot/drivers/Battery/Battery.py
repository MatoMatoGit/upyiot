from micropython import const
from machine import Pin, ADC


class Battery(object):
    
    LIPO_VOLT_TO_PERCENT_CURVE = (4.4, 3.9, 3.75, 3.7, 3.65, 3)
    LIPO_VOLT_TO_PERCENT_STEP = const(25)
    
    def __init__(self, num_cells, volt_pin_nr):
        self.NumCells = num_cells
        self.BatVoltageAdc = ADC(Pin(volt_pin_nr))
        self.BatVoltageAdc.atten(ADC.ATTN_11DB)
        self.BatVoltageAdc.width(ADC.WIDTH_10BIT)
        self.Level = 100
    
    def LevelRead(self):
        # Read the current battery voltage and convert it to a percentage.
        volt = Battery.BatVoltageAdc.read()
        Battery.Level = Battery.VoltageToPercent(volt)
        return Battery.Level
       
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
