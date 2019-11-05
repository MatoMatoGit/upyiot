from machine import Pin

class TactSwitch:

    CALLBACK_PRESSED    = const(0)
    CALLBACK_RELEASED   = const(1)
    CALLBACK_HOLD       = const(2)

    def __init__(self, tact_sw_pin, callbacks, wake_on_press=False):
        if wake_on_press is False:
            wake_param = None
        else:
            wake_param = machine.DEEPSLEEP

        self.TactSwPin = Pin(tact_sw_pin, mode=Pin.IN)
        self.TactSwPin.irq(trigger=(Pin.IRQ_RISING | Pin.IRQ_FALLING), handler=self._IrqHandlerTactSwPin,
                           wake=wake_param, hard=True)

    @staticmethod
    def _IrqHandlerTactSwPin(pin_obj):
        return

