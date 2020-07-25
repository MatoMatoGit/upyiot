import time


class WaterPump:

    def __init__(self, supply, ml_per_min):
        self.CapacityMlPerMin = ml_per_min
        self.Supply = supply
        return

    def PumpAmount(self, amount_ml):
        self.Enable()
        time.sleep(self._MlToSec(amount_ml))
        self.Disable()
        return

    def PumpDuration(self, t_sec):
        self.Enable()
        time.sleep(self._MlToSec(t_sec * 1000))
        self.Disable()
        return

    def Enable(self):
        self.Supply.Enable()
        return

    def Disable(self):
        self.Supply.Disable()
        return

    def DurationSecGet(self, amount_ml):
        return self._MlToSec(amount_ml)

    def _MlToSec(self, amount_ml):
        minutes = amount_ml / self.CapacityMlPerMin
        return minutes * 60

    def IsEnabled(self):
        return self.Supply.IsEnabled()
