from SubjectObserver import Observer
from lib import RgbLed
import uasyncio

class MoistureObserver(Observer):
     
    def __init__(self):
        super().__init__()
        self.MoistureLevel = 0
                                                                                                                                                                             
    def Update(self, arg):
        self.MoistureLevel = arg
    
    
class Notifyer(object):
    
    NOTIFICATION_INTERVAL_SEC = 120
    
    def __init__(self, color_mapping):
        super().__init__()
        self.Moisture = MoistureObserver()
    
    
    def MoistureObserver(self):
        return self.Moisture

    def NotifyLowBattery(self):
        return 0
        
    @staticmethod
    async def NotifyerService():
        RgbLed.Color(Notifyer.__MapParametersToColors(
            Notifyer.Moisture.MoistureLevel))
        await uasyncio.sleep(Notifyer.NOTIFICATION_INTERVAL_SEC)
    
    @staticmethod
    def __MapParametersToColors(moisture):
        return (0, 0, moisture)
    