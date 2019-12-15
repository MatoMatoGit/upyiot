from micropython import const
from machine import Pin, ADC
from upyiot.drivers.Sensors.SensorBase import SensorBase
import utime


class BatteryLevel(SensorBase):
    
    LIPO_VOLT_TO_PERCENT_CURVE = (4.4, 3.9, 3.75, 3.7, 3.65, 3)
    LIPO_VOLT_TO_PERCENT_STEP = const(25)
    ADC_REF_VOLTAGE = 3.3
    ADC_RES_BITS = const(10)
    BAT_VOLT_MULTIPLIER = const(2)  # Multiplier is due to the on-board 10K/10K voltage divider.
    
    def __init__(self, num_cells, volt_pin_nr, en_pin_nr):
        self.NumCells = num_cells
        self.BatVoltageEnable = Pin(en_pin_nr, Pin.OUT)
        self.BatVoltageAdc = ADC(Pin(volt_pin_nr))
        self.BatVoltageAdc.atten(ADC.ATTN_11DB)
        self.BatVoltageAdc.width(ADC.WIDTH_10BIT)
        self.Level = 0
    
    def Read(self):
        self.BatVoltageEnable.on()
        utime.sleep_ms(500)
        # Read the current battery voltage and convert it to a percentage.
        raw = self.BatVoltageAdc.read()
        self.BatVoltageEnable.off()
        print("Battery raw adc: {}".format(raw))

        volt = BatteryLevel.RawAdcValueToVoltage(self.ADC_REF_VOLTAGE, self.ADC_RES_BITS,
                                                 self.BAT_VOLT_MULTIPLIER, raw)
        print("Battery voltage: {}V".format(volt))

        self.Level = self.VoltageToPercent(volt)
        print("Battery level: {}%".format(self.Level))
        return self.Level

    @staticmethod
    def RawAdcValueToVoltage(ref_volt, adc_res_bits, mult, val):
        val = val * mult
        val = val * (ref_volt / pow(2, adc_res_bits))
        return val

    @staticmethod
    def VoltageToPercent(volt):
        if volt > BatteryLevel.LIPO_VOLT_TO_PERCENT_CURVE[0]:
            return 100
        i = 0
        # Loop through the battery curve until the measured voltage
        # is higher than the curve value.
        for v in BatteryLevel.LIPO_VOLT_TO_PERCENT_CURVE:
            if volt > v:
                break;
            i = i + 1
        # The drained percentage is equal to the number of steps - 1 (if 1
        # step is taken the battery is considered to be full) times
        # the percentage per step.
        return 100 - ((i - 1) * BatteryLevel.LIPO_VOLT_TO_PERCENT_STEP)
