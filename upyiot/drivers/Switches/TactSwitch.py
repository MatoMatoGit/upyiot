from machine import Pin, Timer
import machine


class TactSwitch:

    CALLBACK_PRESSED    = const(0)
    CALLBACK_RELEASED   = const(1)
    CALLBACK_HOLD       = const(2)
    NUM_CALLBACKS       = const(3)

    UserCallbacks = None
    HoldTimer = None
    HoldTime = 0
    HoldTimerCallback = None

    def __init__(self, tact_sw_pin, callbacks, hold_time, wake_on_press=False):
        if len(callbacks < TactSwitch.NUM_CALLBACKS):
            raise ValueError
        TactSwitch.UserCallbacks = callbacks

        if callbacks[TactSwitch.CALLBACK_HOLD] is not None and hold_time > 0:
            TactSwitch.HoldTimer = Timer(-1)
            TactSwitch.HoldTimerCallback = self._HoldTimerCallback

        if wake_on_press is False:
            wake_param = None
        else:
            wake_param = machine.DEEPSLEEP

        self.TactSwPin = Pin(tact_sw_pin, mode=Pin.IN)
        self.TactSwPin.irq(trigger=(Pin.IRQ_RISING | Pin.IRQ_FALLING),
                           handler=self._IrqHandlerTactSwPin,
                           wake=wake_param, hard=True)

    @staticmethod
    def _IrqHandlerTactSwPin(pin_obj):
        if pin_obj.value() is 1:
            TactSwitch._HoldTimerStart()
            TactSwitch._ScheduleCallback(TactSwitch.CALLBACK_PRESSED)
        else:
            TactSwitch.HoldTimer.deinit()
            TactSwitch._ScheduleCallback(TactSwitch.CALLBACK_RELEASED)
        return

    def _HoldTimerCallback(self, timer):
        TactSwitch._ScheduleCallback(TactSwitch.CALLBACK_HOLD)

    @staticmethod
    def _ScheduleCallback(callback_type):
        if TactSwitch.UserCallbacks[callback_type] is not None:
            micropython.schedule(TactSwitch.UserCallbacks[callback_type])

    @staticmethod
    def _HoldTimerStart():
        TactSwitch.HoldTimer.init(period=TactSwitch.HoldTime,
                                  mode=Timer.ONE_SHOT,
                                  callback=TactSwitch.HoldTimerCallback)
