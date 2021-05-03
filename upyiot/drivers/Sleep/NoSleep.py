from upyiot.drivers.Sleep.DeepSleepBase import DeepSleepBase
import utime
import machine


class NoSleep(DeepSleepBase):

    def DeepSleep(self, msec):
        print("[NoSleep] Idle for {}".format(msec))
        utime.sleep(int(msec/1000))
        machine.reset()

    def DeepSleepForever(self):
        while True:
            utime.sleep(10)