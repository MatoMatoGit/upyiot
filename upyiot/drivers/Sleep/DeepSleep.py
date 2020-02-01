try:
    import machine
except:
    from stubs import machine
from micropython import const


class DeepSleepExceptionInitiated(Exception):

    def __init__(self):
        super().__init__()


class DeepSleep:

    WAKE_REASON_RESET = const(0)
    WAKE_REASON_PIN   = const(1)
    WAKE_REASON_RTC   = const(2)

    def __init__(self):
        # Create a set for all BeforeSleep callbacks.
        self.CbsBeforeSleep = set()

    def WakeReason(self):
        # Check the wake-reason to determine if the device was
        # woken from sleep.
        if machine.reset_cause() is machine.DEEPSLEEP_RESET:
            if machine.wake_reason() is machine.PIN_WAKE:
                return DeepSleep.WAKE_REASON_PIN
            else:
                return DeepSleep.WAKE_REASON_RTC
        else:
            return DeepSleep.WAKE_REASON_RESET

    def RegisterCallbackBeforeDeepSleep(self, callback):
        self.CbsBeforeSleep.add(callback)

    def DeepSleep(self, msec):
        print("[DeepSleep] Going to sleep for {} msec.".format(msec))
        # Notify all registered callbacks
        self._NotifyBeforeDeepSleep()
        machine.deepsleep(msec)
        raise DeepSleepExceptionInitiated

    def DeepSleepForever(self):
        # Notify all registered callbacks
        self._NotifyBeforeDeepSleep()
        machine.deepsleep()

    def _NotifyBeforeDeepSleep(self):
        for cb in self.CbsBeforeSleep:
            cb()

    @staticmethod
    def WakeReasonToString(wake_reason):
        if wake_reason is DeepSleep.WAKE_REASON_RESET:
            return "Reset"
        elif wake_reason is DeepSleep.WAKE_REASON_RTC:
            return "RTC"
        elif wake_reason is DeepSleep.WAKE_REASON_PIN:
            return "Pin"
        else:
            return "Unknown"
