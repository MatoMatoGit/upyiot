from upyiot.drivers.Sensors.SensorBase import SensorBase
import esp32


class InternalTemp(SensorBase):

    def __init__(self):
        return

    def Read(self):
        temp_f = esp32.raw_temperature()
        temp_c = (temp_f - 32.0) / 1.8
        print("T = {0:4d} deg F or {1:5.1f}  deg C".format(temp_f, temp_c))
        return temp_c

    def Enable(self):
        pass

    def Disable(self):
        pass
