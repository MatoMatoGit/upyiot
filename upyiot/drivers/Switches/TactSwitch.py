from machine import Pin, Timer
import machine
import micropython
import esp32



class TactSwitch:

    CALLBACK_PRESSED    = const(0)
    CALLBACK_RELEASED   = const(1)
    NUM_CALLBACKS       = const(2)

    DEBOUNCE_TIME_MS    = const(100)

    PIN_VALUE_PRESSED   = const(0)

    UserCallbacks = None
    HoldTimer = None
    HoldTimes = 0
    HoldTimerCallback = None
    HoldIndex = 0
    DebounceTimer = None
    DebounceTimerCallback = None

    def __init__(self, tact_sw_pin_nr, callbacks, hold_times, wake_on_press=False):
        """

        :param tact_sw_pin_nr: Tactile switch pin number.
        :param callbacks: Callbacks tuple, must contain 2 callbacks.
        :param hold_times: Hold times tuple. If no hold times are used
        pass (0, ).
        :param wake_on_press: The tactile switch is configured as a wake-up source if True.
        Default is False.
        """
        if len(callbacks) < TactSwitch.NUM_CALLBACKS:
            raise ValueError
        TactSwitch.UserCallbacks = callbacks

        if hold_times[0] > 0:
            TactSwitch.HoldTimer = Timer(-1)
            TactSwitch.HoldTimerCallback = self._HoldTimerCallback
            TactSwitch.HoldTimes = hold_times

        TactSwitch.DebounceTimer = Timer(-1)
        TactSwitch.DebounceTimerCallback = self._DebounceTimerCallback

        if wake_on_press is False:
            wake_param = None
        else:
            wake_param = machine.DEEPSLEEP

        self.TactSwPin = Pin(tact_sw_pin_nr, mode=Pin.IN)
        self.TactSwPin.irq(trigger=(Pin.IRQ_RISING | Pin.IRQ_FALLING),
                           handler=self._IrqHandlerTactSwPin,
                           wake=wake_param)
        esp32.wake_on_ext0(pin=self.TactSwPin, level=esp32.WAKEUP_ALL_LOW)

        self.Enabled = False

    def Enable(self):
        self.Enabled = True

    def Disable(self):
        self.Enabled = False

    @staticmethod
    def _IrqHandlerTactSwPin(pin_obj):
        if TactSwitch.Enabled is True:
            TactSwitch._DebounceTimerStart()

    def _HoldTimerCallback(self, timer):
        TactSwitch.HoldIndex += 1
        if (TactSwitch.HoldIndex + 1) < len(TactSwitch.HoldTimes):
            TactSwitch._HoldTimerStart(TactSwitch.HoldTimes[TactSwitch.HoldIndex + 1])

    @staticmethod
    def _ScheduleCallback(callback_type):
        if TactSwitch.UserCallbacks[callback_type] is not None:
            micropython.schedule(TactSwitch.UserCallbacks[callback_type], TactSwitch.HoldIndex)
            TactSwitch.HoldIndex = -1

    @staticmethod
    def _HoldTimerStart(time_ms):
        TactSwitch.HoldTimer.init(period=TactSwitch.HoldTimes[time_ms],
                                  mode=Timer.ONE_SHOT,
                                  callback=TactSwitch.HoldTimerCallback)
    @staticmethod
    def _HoldTimerStop():
        try:
            TactSwitch.HoldTimer.deinit()
        except:
            print("[TactSw] No hold timer running.")


    @staticmethod
    def _DebounceTimerStart():
        try:
            TactSwitch.DebounceTimer.deinit()
        except:
            print("[TactSw] No debounce timer running.")

        TactSwitch.DebounceTimer.init(period=TactSwitch.DEBOUNCE_TIME_MS,
                                      mode=Timer.ONE_SHOT,
                                      callback=TactSwitch._DebounceTimerCallback)

    def _DebounceTimerCallback(self, timer):
        if self.TactSwPin.value() is self.PIN_VALUE_PRESSED:
            TactSwitch.HoldIndex = -1
            TactSwitch._HoldTimerStart(TactSwitch.HoldTimes[0])
            TactSwitch._ScheduleCallback(TactSwitch.CALLBACK_PRESSED)
        else:
            TactSwitch._HoldTimerStop()
            TactSwitch._ScheduleCallback(TactSwitch.CALLBACK_RELEASED)
