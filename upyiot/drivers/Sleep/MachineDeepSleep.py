try:
    import machine
except:
    from stubs import machine
from upyiot.drivers.Sleep.DeepSleepBase import DeepSleepExceptionFailed
from upyiot.drivers.Sleep.DeepSleepBase import DeepSleepBase


class MachineDeepSleep(DeepSleepBase):

    def __init__(self):
        return

    def DeepSleep(self, msec):
        print("[DeepSleep] Going to sleep for {} msec.".format(msec))
        if msec is not 0:
            machine.deepsleep(msec)
        else:
            self.DeepSleepForever()

        raise DeepSleepExceptionFailed

    def DeepSleepForever(self):
        machine.deepsleep()



