from machine import Pin, Timer
import machine
import micropython
import esp32


class TactSwitch:

    TIMER_DEBOUNCE      = const(0)
    TIMER_HOLD_REST     = const(1)
    NUM_TIMERS          = const(2)

    CALLBACK_PRESSED    = const(0)
    CALLBACK_RELEASED   = const(1)

    NUM_CALLBACKS       = const(2)

    CALLBACK_ARG_PRESS_COUNT = const(0)
    CALLBACK_ARG_HOLD_INDEX  = const(1)

    DEBOUNCE_TIME_MS    = const(50)

    PIN_VALUE_PRESSED   = const(0)
    PIN_VALUE_RELEASED = const(1)

    UserCallbacks = None
    PressTimer = None
    PressCount = 0
    State = PIN_VALUE_RELEASED

    HoldTimes = 0
    HoldTime = 0
    HoldCallback = None
    HoldIndex = 0

    RestCallback = None
    RestTime = 500
    DebounceTimer = None
    DebouceTimerRunning = False
    DebounceTimerCallback = None

    Enabled = False
    TactSwPin = None

    def __init__(self, tact_sw_pin_nr, timer_nrs, callbacks, hold_times_ms, rest_time_ms, wake_on_press=False):
        """

        :param tact_sw_pin_nr: Tactile switch pin number.
        :param timer_nrs: Timer numbers used for debounce and hold/rest respectively.
        :param callbacks: Callbacks tuple, must contain 2 callbacks.
        :param hold_times_ms: Hold times (ms) tuple. If no hold times are used
        pass (0, ).
        :param rest_time_ms: Time it takes to reset the press count in ms.
        :param wake_on_press: The tactile switch is configured as a wake-up source if True.
        Default is False.
        """

        if len(timer_nrs) < TactSwitch.NUM_TIMERS:
            raise ValueError

        if len(callbacks) < TactSwitch.NUM_CALLBACKS:
            raise ValueError

        TactSwitch.UserCallbacks = callbacks

        TactSwitch.PressTimer = Timer(timer_nrs[TactSwitch.TIMER_HOLD_REST])

        if hold_times_ms[0] > 0:
            TactSwitch.HoldCallback = TactSwitch._HoldCallback
            TactSwitch.HoldTimes = hold_times_ms

        TactSwitch.RestCallback = TactSwitch._RestCallback
        TactSwitch.RestTime = rest_time_ms
        TactSwitch.DebounceTimer = Timer(timer_nrs[TactSwitch.TIMER_DEBOUNCE])
        TactSwitch.DebounceTimerCallback = TactSwitch._DebounceTimerCallback

        if wake_on_press is False:
            wake_param = None
        else:
            wake_param = machine.DEEPSLEEP

        TactSwitch.TactSwPin = Pin(tact_sw_pin_nr, mode=Pin.IN)
        TactSwitch.TactSwPin.irq(trigger=(Pin.IRQ_RISING | Pin.IRQ_FALLING),
                                 handler=self._IrqHandlerTactSwPin,
                                 wake=wake_param)
        esp32.wake_on_ext0(pin=self.TactSwPin, level=esp32.WAKEUP_ALL_LOW)

        TactSwitch.Enabled = False

    def Enable(self):
        TactSwitch.Enabled = True
        if self.IsPressed() and TactSwitch.State is self.PIN_VALUE_RELEASED:
            TactSwitch._IrqHandlerTactSwPin(self.TactSwPin)


    def Disable(self):
        TactSwitch.Enabled = False

    def IsPressed(self):
        return TactSwitch.TactSwPin.value() is self.PIN_VALUE_PRESSED

    @staticmethod
    def _IrqHandlerTactSwPin(pin_obj):
        if TactSwitch.Enabled is True:
            TactSwitch._DebounceTimerStart()

    @staticmethod
    def _ScheduleCallback(callback_type, *args):
        if TactSwitch.UserCallbacks[callback_type] is not None:
            micropython.schedule(TactSwitch.UserCallbacks[callback_type], (args[TactSwitch.CALLBACK_ARG_PRESS_COUNT],
                                                                           args[TactSwitch.CALLBACK_ARG_HOLD_INDEX]))
            TactSwitch.HoldIndex = -1

    @staticmethod
    def _HoldCallback(timer):
        TactSwitch.HoldIndex += 1
        TactSwitch.HoldTime += TactSwitch.HoldTimes[TactSwitch.HoldIndex] - TactSwitch.HoldTime
        print("[TactSw] Hold index: {}".format(TactSwitch.HoldIndex))
        print("[TactSw] Hold time: {}".format(TactSwitch.HoldTime))

        if (TactSwitch.HoldIndex + 1) < len(TactSwitch.HoldTimes):
            hold_time = TactSwitch.HoldTimes[TactSwitch.HoldIndex + 1] - TactSwitch.HoldTime
            TactSwitch._HoldTimerStart(hold_time)

    @staticmethod
    def _HoldTimerStart(time_ms):
        if time_ms is 0:
            return

        print("[TactSw] Starting hold timer: {}ms".format(time_ms))
        try:
            TactSwitch.PressTimer.init(period=time_ms,
                                       mode=Timer.ONE_SHOT,
                                       callback=TactSwitch.HoldCallback)
        except OSError:
            print("[TactSw] Failed to start hold timer.")

    @staticmethod
    def _HoldTimerStop():
        try:
            TactSwitch.PressTimer.deinit()
        except OSError:
            print("[TactSw] No hold timer running.")


    @staticmethod
    def _RestCallback(timer):
        TactSwitch.State = TactSwitch.PIN_VALUE_RELEASED
        TactSwitch._ScheduleCallback(TactSwitch.CALLBACK_RELEASED, TactSwitch.PressCount, TactSwitch.HoldIndex)
        TactSwitch.PressCount = 0

    @staticmethod
    def _RestTimerStart():
        print("[TactSw] Starting rest timer: {}ms".format(TactSwitch.RestTime))
        try:
            TactSwitch.PressTimer.init(period=TactSwitch.RestTime,
                                      mode=Timer.ONE_SHOT,
                                      callback=TactSwitch.RestCallback)
        except OSError:
            print("[TactSw] Failed to start rest timer.")

    @staticmethod
    def _RestTimerStop():
        try:
            TactSwitch.PressTimer.deinit()
        except OSError:
            print("[TactSw] No reset timer running.")


    @staticmethod
    def _DebounceTimerStart():
        try:
            TactSwitch.DebounceTimer.deinit()
        except OSError:
            print("[TactSw] No debounce timer running.")

        print("---------------------")
        print("[TactSw] Press count: {}".format(TactSwitch.PressCount))
        print("[TactSw] Debounce start.")
        TactSwitch.DebounceTimer.init(period=TactSwitch.DEBOUNCE_TIME_MS,
                                      mode=Timer.ONE_SHOT,
                                      callback=TactSwitch.DebounceTimerCallback)

    @staticmethod
    def _DebounceTimerCallback(timer):
        print("[TactSw] Debounced")
        print("[TactSw] State: {}".format(TactSwitch.TactSwPin.value()))
        if TactSwitch.TactSwPin.value() is TactSwitch.PIN_VALUE_PRESSED:
            TactSwitch._HandlePress()
        else:
            TactSwitch._HandleRelease()

    @staticmethod
    def _HandlePress():
        TactSwitch.State = TactSwitch.PIN_VALUE_PRESSED
        TactSwitch._RestTimerStop()
        TactSwitch.HoldTime = 0
        TactSwitch.HoldIndex = -1
        TactSwitch._HoldTimerStart(TactSwitch.HoldTimes[0])
        TactSwitch._ScheduleCallback(TactSwitch.CALLBACK_PRESSED, TactSwitch.PressCount, TactSwitch.HoldIndex)

    @staticmethod
    def _HandleRelease():
        TactSwitch._HoldTimerStop()
        TactSwitch.PressCount += 1
        TactSwitch._RestTimerStart()
