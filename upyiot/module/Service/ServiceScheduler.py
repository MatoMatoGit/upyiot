from upyiot.module.Service.Service import Service
from upyiot.module.Service.Service import ServiceExceptionSuspend
from upyiot.module.Service.Service import ServiceException
import utime
from micropython import const


class SchedulerException(Exception):

    def __init__(self):
        return


class SchedulerExceptionStopped(SchedulerException):

    def __init__(self):
        return


class ServiceScheduler:

    SCHEDULER_RESULT_OK = const(0)
    SCHEDULER_RESULT_ERR = const(-1)

    def __init__(self, sleep_time_sec=1):
        self.Services = list()
        self.RunTimeSec = 0
        self.Cycles = None
        self.Index = 0
        self.SleepTimeSec = sleep_time_sec
        return

    def ServiceRegister(self, service):
        res = 0
        try:
            if service.SvcIsInitialized() is False:
                service.SvcInit()
                service.SvcStateSet(Service.STATE_SUSPENDED)
                self.Services.append(service)
        except:
            service.SvcStateSet(Service.STATE_DISABLED)
            res = -1

        return res

    def ServiceDeregister(self, service):
        res = 0
        try:
            if service.SvcIsInitialized() is True:
                service.SvcDeinit()
                service.SvcStateSet(Service.STATE_UNINITIALIZED)
        except:
            service.SvcStateSet(Service.STATE_DISABLED)
            res = -1
        finally:
            self.Services.remove(service)
        return res

    def Run(self, cycles=None):
        self.Cycles = cycles

        try:
            # Infinite loop
            while True:
                self._UpdatePeriodicServices()

                # Service run loop.
                # Runs a service until none are ready.
                self.Index = 0
                while True:
                    svc_ran = False

                    if self.Index >= len(self.Services):
                        print("[Scheduler] No services registered")
                        break

                    service = self.Services[self.Index]

                    if service.SvcStateGet() is not service.STATE_DISABLED:
                        print("[Scheduler] Selected service: {}".format(service))
                        # Check if all services that this service is dependent on
                        # ran at least once. If this is the case the service is ready
                        # to run.
                        if service.SvcIsActive() and self._CheckServiceDependencies(service) is True:
                            service.SvcStateSet(Service.STATE_READY)

                        # If the service is ready to run, call its Run method.
                        if service.SvcIsReady() is True:
                            print("[Scheduler] Running service")
                            svc_ran = True
                            self._ServiceRun(service)
                    else:
                        print("[Scheduler] Service {} is disabled".format(service))

                    print("[Scheduler] Selecting next service")
                    if self._IndexAdvance(svc_ran) is False:
                        print("[Scheduler] No more services to run")
                        break
                    print("[Scheduler] Next index: {}".format(self.Index))

                self.RunTimeSec += 1
                print("[Scheduler] Sleeping for {} seconds".format(self.SleepTimeSec))
                # No services are ready at this moment.
                utime.sleep(self.SleepTimeSec)

                self._CyclesDec()

        except SchedulerExceptionStopped:
            print("[Scheduler] Stopped.")

    def _ServiceRun(self, service):
        try:
            service.SvcRun()
            service.SvcStateSet(Service.STATE_SUSPENDED)
        except ServiceExceptionSuspend:
            print("[Scheduler] Suspending service")
            service.SvcStateSet(Service.STATE_SUSPENDED)
        except ServiceException:
            print("[Scheduler] Error occurred, disabling service.")
            service.SvcStateSet(Service.STATE_DISABLED)

        # Update the last run timestamp.
        service.SvcLastRunSet(self.RunTimeSec)
        service.SvcDeactivate()

    def _UpdatePeriodicServices(self):
        # Activate periodic services.
        for svc in self.Services:
            if svc.SvcMode is Service.MODE_RUN_PERIODIC:
                print("[Scheduler] Updating periodic service: {}".format(svc))
                # If interval time has passed, activate the service.
                if self.RunTimeSec + svc.SvcLastRun >= svc.SvcInterval:
                    print("[Scheduler] Activating periodic service: {}".format(svc))
                    svc.SvcActivate()

    def _CheckServiceDependencies(self, service):
        ready = True
        for svc_dep in service.SvcDeps:
            print("[Scheduler] Checking dependency: {}".format(svc_dep))
            if svc_dep.SvcLastRun is 0:
                svc_dep.SvcActivate()
                ready = False
        print("[Scheduler] Dependencies ran: {}".format(ready))
        return ready

    def _IndexAdvance(self, svc_ran):
        print("[Scheduler] Service ran: {}".format(svc_ran))
        # Increment the service list index.
        # Wrap around if the end if reached.
        self.Index += 1

        if self.Index >= len(self.Services):
            self.Index = 0
            # A minimum of one service must
            # have ran.
            return svc_ran

        return True

    def _CyclesDec(self):
        if self.Cycles is not None:
            self.Cycles -= 1
            print("[Scheduler] Cycles left: {}.".format(self.Cycles))
            if self.Cycles is 0:
                raise SchedulerExceptionStopped
