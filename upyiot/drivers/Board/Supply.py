from machine import Pin, Signal
import utime
from micropython import const


class Supply:

    SUPPLY_STATE_DISABLED = const(0)
    SUPPLY_STATE_ENABLED = const(1)

    def __init__(self, en_pin_nr, settle_time_ms, inverse_pol=False, default_state=SUPPLY_STATE_DISABLED):
        self.EnPin = Signal(en_pin_nr, mode=Pin.OUT, invert=inverse_pol)

        if default_state is self.SUPPLY_STATE_ENABLED:
            self.Enable()
        else:
            self.EnCount = 0
            self.EnPin.off()

        self.SettleTime = settle_time_ms

    def Enable(self):
        self.EnCount += 1
        print("[Supply] Enable count: {}".format(self.EnCount))

        if self.EnCount is 1:
            print("[Supply] Enabling supply")
            self.EnPin.on()
            utime.sleep_ms(self.SettleTime)
        return 0

    def Disable(self):
        if self.EnCount is 0:
            print("[Supply] Supply cannot be disabled")
            return -1

        self.EnCount -= 1
        print("[Supply] Enable count: {}".format(self.EnCount))

        if self.EnCount is 0:
            print("[Supply] Disabling supply")
            self.EnPin.off()
            utime.sleep_ms(self.SettleTime)

        return 0

    def IsEnabled(self):
        return self.EnCount > 0
