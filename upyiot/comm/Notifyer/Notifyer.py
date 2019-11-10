from upyiot.middleware.SubjectObserver import Observer
from upyiot.drivers.Led.RgbLed import RgbLed
import uasyncio


class MoistureObserver(Observer):
     
    def __init__(self):
        super().__init__()
        self.MoistureLevel = 0
                                                                                                                                                                             
    def Update(self, arg):
        self.MoistureLevel = arg
    
    
class Notifyer(object):
    
    def __init__(self, color_mapping, rgbled_obj):
        super().__init__()
        self.Moisture = MoistureObserver()
        self.RgbLed = rgbled_obj
    
    
    def MoistureObserver(self):
        return self.Moisture

    def NotifyLowBattery(self):
        return 0
        
    @staticmethod
    async def Service(t_sleep_sec):
        Notifyer.RgbLed.Color(Notifyer._MapParametersToColors(
            Notifyer.Moisture.MoistureLevel))
        await uasyncio.sleep(t_sleep_sec)
    
    @staticmethod
    def _MapParametersToColors(moisture):
        return (0, 0, moisture)
