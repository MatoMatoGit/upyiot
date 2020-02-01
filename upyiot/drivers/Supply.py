import Pin, Signal
import utime
from micropython import const

class Supply:

    SUPPLY_STATE_DISABLED = const(0)
    SUPPLY_STATE_ENABLED = const(1)

    def __init__(self, en_pin_nr, settle_time_ms, inverse_pol=False, default_state=SUPPLY_STATE_DISABLED):
        if default_state is self.SUPPLY_STATE_ENABLED:
            self.EnCount = 1
        else:
            self.EnCount = 0

        self.EnPin = Signal(Pin(en_pin_nr, mode=Pin.OUT), inverse_pol)
        self.SettleTime = settle_time_ms

    def Enable(self):
        if self.EnCount is 0:
            self.EnPin.on()
            utime.sleep_ms(self.SettleTime)

        self.EnCount += 1
        return 0

    def Disable(self):
        if self.EnCount is 0:
            return -1

        self.EnCount -= 1
        if self.EnCount is 0:
            self.EnPin.off()
            utime.sleep_ms(self.SettleTime)

        return 0

    def IsEnabled(self):
        return self.EnCount > 0
