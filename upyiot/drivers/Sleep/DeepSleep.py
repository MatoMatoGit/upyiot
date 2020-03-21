try:
    import machine
except:
    from stubs import machine
from micropython import const


class DeepSleepExceptionInitiated(Exception):

    def __init__(self):
        super().__init__()


class DeepSleep:

    def __init__(self):
        # Create a set for all BeforeSleep callbacks.
        self.CbsBeforeSleep = set()

    def RegisterCallbackBeforeDeepSleep(self, callback):
        self.CbsBeforeSleep.add(callback)

    def DeepSleep(self, msec):
        print("[DeepSleep] Going to sleep for {} msec.".format(msec))
        if msec is not 0:
            # Notify all registered callbacks
            self._NotifyBeforeDeepSleep()
            machine.deepsleep(msec)
        else:
            self.DeepSleepForever()

        raise DeepSleepExceptionInitiated

    def DeepSleepForever(self):
        # Notify all registered callbacks
        self._NotifyBeforeDeepSleep()
        machine.deepsleep()

    def _NotifyBeforeDeepSleep(self):
        for cb in self.CbsBeforeSleep:
            cb()

