from upyiot.system.Service.Service import Service
from upyiot.system.Service.Service import ServiceExceptionSuspend
from upyiot.system.Service.Service import ServiceException
from upyiot.drivers.Sleep.DeepSleep import DeepSleep
from upyiot.middleware.StructFile.StructFile import StructFile

import utime
from micropython import const


class SchedulerException(Exception):

    def __init__(self):
        return


class SchedulerExceptionStopped(SchedulerException):

    def __init__(self):
        return


class SchedulerExceptionDeepSleepFailed(SchedulerException):

    def __init__(self):
        return


class SchedulerMemory:

    FILE_SCHEDULER_MEMORY = "/sched_mem"
    SVC_MEM_FMT = "<20sI"
    SCHED_MEM_FMT = "<III"

    SCHED_MEM_RUNTIME = const(0)
    SCHED_MEM_SLEEPTIME = const(1)
    SCHED_MEM_NUM_SVC = const(2)

    SVC_MEM_NAME = const(0)
    SVC_MEM_LAST_RUN = const(1)

    def __init__(self, directory, scheduler_obj):
        self.Sfile = StructFile(directory + self.FILE_SCHEDULER_MEMORY,
                                self.SVC_MEM_FMT,
                                self.SCHED_MEM_FMT)
        self.Scheduler = scheduler_obj
        self.NumEntries = 0

    def Save(self):
        # Clear the memory.
        self.Sfile.Clear()

        # Iterate through all registered services and store their data.
        i = 0
        for svc in self.Scheduler.Services:
            print("[SchedulerMem] Writing data for service {}".format(svc.SvcName))
            self.Sfile.WriteData(i, svc.SvcName, svc.SvcLastRun)
            i += 1

        self.NumEntries = i
        print("[SchedulerMem] Total number of service entries: {}".format(self.NumEntries))
        # Store the scheduler data (in the StructFile meta).
        print("[SchedulerMem] Writing scheduler data")
        self.Sfile.WriteMeta(self.Scheduler.RunTimeSec, self.Scheduler.SleepTime,
                             self.NumEntries)
        return 0

    def Load(self):
        # Load the scheduler data first (from the StructFile meta).
        sched_mem = self.Sfile.ReadMeta()
        print(sched_mem)
        if sched_mem is not None:
            self.Scheduler.RunTimeSec = sched_mem[self.SCHED_MEM_RUNTIME]
            self.Scheduler.SleepTime = sched_mem[self.SCHED_MEM_SLEEPTIME]
            self.NumEntries = sched_mem[self.SCHED_MEM_NUM_SVC]
        else:
            return -1

        self.Sfile.IteratorConfig(0, 0, self.NumEntries)

        # Iterate through the set of stored service data and restore
        # the data if a matching service is found (by name).
        for svc_mem in self.Sfile:
            svc_name = svc_mem[self.SVC_MEM_NAME].decode('utf-8').split('\0')[0]
            print("[SchedulerMem] Read data for service: {}".format(svc_name))
            idx = self.Sfile.IteratorIndex()
            if idx < len(self.Scheduler.Services):
                # First service to check if the one at the same index as it was stored at.
                # The chance is very high that the services were registered in the same order.
                svc = self.Scheduler.Services[idx]
                print("[SchedulerMem] Same-index service {}".format(svc.SvcName))
                if svc.SvcName == svc_name:
                    self._LoadService(svc, svc_mem)
                    continue
                else:
                    svc = self._SearchService(svc_name)
                    self._LoadService(svc, svc_mem)
                    continue

            # If the service does not match the same index, iterate
            # through the registered services to find a name match.
            else:
                svc = self._SearchService(svc_name)
                self._LoadService(svc, svc_mem)
                continue

        print("[SchedulerMem] Finished loading memory.")
        return 0

    def _LoadService(self, svc, svc_mem):
        if svc is None:
            return
        svc.SvcLastRun = svc_mem[self.SVC_MEM_LAST_RUN]

    def SearchAndLoadService(self, name):
        self.Sfile.IteratorConfig(0, self.NumEntries)

        # Iterate through the set of stored service data and restore
        # the data if a matching service is found (by name).
        for svc_mem in self.Sfile:
            if svc_mem[self.SVC_MEM_NAME] == name:
                for svc in self.Scheduler.Services:
                    if svc.SvcName == name:
                        svc.SvcLastRun = svc_mem[self.SVC_MEM_LAST_RUN]
                        return 0
        return -1

    def _SearchService(self, name):
        print("[SchedulerMem] Searching service: {}".format(name))
        for svc in self.Scheduler.Services:
            print(svc)
            if svc.SvcName == name:
                return svc
        return None


class ServiceScheduler:

    SCHEDULER_RESULT_OK     = const(0)
    SCHEDULER_RESULT_ERR    = const(-1)
    MIN_DEEPSLEEP_TIME      = const(10)

    def __init__(self, idle_time_sec=1, directory="./"):
        self.Services = list()
        self.RunTimeSec = 0
        self.Cycles = None
        self.Index = 0
        self.IdleTimeSec = idle_time_sec
        self.DeepSleep = DeepSleep()
        self.SleepTime = 0
        self.Memory = SchedulerMemory(directory, self)

        return

    def ServiceRegister(self, service):
        res = 0
        try:
            if service.SvcIsInitialized() is False:
                service.SvcInit()
                service.SvcStateSet(Service.STATE_SUSPENDED)
                self.Services.append(service)
                print("[Scheduler] Registered service: {}".format(service.SvcName))
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
                print("[Scheduler] Deregistered service: {}".format(service.SvcName))
        except:
            service.SvcStateSet(Service.STATE_DISABLED)
            res = -1
        finally:
            self.Services.remove(service)
        return res

    def Run(self, cycles=None):

        # Load the scheduler run time, and last-run time of all services.
        self.Memory.Load()

        self.Cycles = cycles

        print("[Scheduler] ##### Run #####")
        try:
            # Infinite loop
            while True:
                print("\n[Scheduler] ##### Cycles left: {} #####\n".format(self.Cycles))
                # Add the amount time spend sleeping or idling.
                self.RunTimeSec += self.SleepTime

                print("[Scheduler] Run time (s): {}".format(self.RunTimeSec))

                # Save the start time before executing the loop.
                t_start = utime.ticks_ms()

                self.SleepTime = self._UpdatePeriodicServices()
                print("[Scheduler] Shortest sleep time: {}".format(self.SleepTime))

                # Service run loop.
                # Runs a service until none are ready.
                self.Index = 0
                while True:
                    svc_activated = False

                    if self.Index >= len(self.Services):
                        print("[Scheduler] No services registered")
                        break

                    service = self.Services[self.Index]

                    if service.SvcStateGet() is not service.STATE_DISABLED:
                        print("[Scheduler] Checking: {}".format(service.SvcName))
                        # Check if all services that this service is dependent on
                        # ran at least once. If this is the case the service is ready
                        # to run.
                        if service.SvcIsActive() is True:
                            if self._CheckServiceDependencies(service) is False:
                                # If the service depdencency check returns false, it means
                                # there is at least one service that has been activated.
                                svc_activated = True
                            else:
                                print("[Scheduler] Ready: {}".format(service.SvcName))
                                service.SvcStateSet(Service.STATE_READY)

                        # If the service is ready to run, run it.
                        if service.SvcIsReady() is True:
                            print("[Scheduler] Running: {}".format(service.SvcName))
                            svc_activated = True
                            self._ServiceRun(service)
                    else:
                        print("[Scheduler] Disabled: {}".format(service.SvcName))

                    print("[Scheduler] Selecting next service")
                    if self._IndexAdvance(svc_activated) is False:
                        print("[Scheduler] No more services to run")
                        break

                    print("[Scheduler] Next index: {}".format(self.Index))

                # The statements below run after the scheduler finishes executing
                # the services that are ready.

                # Calculate the amount of time that passed while running services.
                t_end = utime.ticks_ms()
                t_ran = utime.ticks_diff(t_end, t_start)
                t_ran_sec = int(round((t_ran / 1000)))

                print("[Scheduler] t start: {}  |"
                      "t_end: {} | t_ran (ms): {} | "
                      "t ran (s): {}".format(t_start,
                                             t_end,
                                             t_ran,
                                             t_ran_sec))

                # Add the amount time that passed since the last update.
                self.RunTimeSec += t_ran_sec

                # Decrease the amount of scheduler cycles left (if applicable).
                self._CyclesDec()

                # If the sleep time is 0 there are no services sleeping.
                if self.SleepTime is 0:
                    self.SleepTime = 1

                # If the shortest sleep time is shorter than the time that
                # has already passed in the previous run loop,
                # run again.
                elif self.SleepTime <= t_ran_sec:
                    continue

                # If the shortest sleep time is shorter than the minimum
                # deepsleep time, than idle instead.
                elif self.SleepTime < ServiceScheduler.MIN_DEEPSLEEP_TIME:
                    print("[Scheduler] Idling for {} seconds".format(self.SleepTime))
                    # No services are ready at this moment.
                    utime.sleep(self.SleepTime)

                # If the shortest sleep time is sufficient for a deepsleep,
                # initiate it.
                else:
                    print("[Scheduler] Initiating deep sleep for {} seconds".format(self.SleepTime))
                    self._InitiateDeepSleep(self.SleepTime)

        except SchedulerExceptionStopped:
            print("[Scheduler] Stopped.")

    def _InitiateDeepSleep(self, t_sec):
        # Save the scheduler run time, and last-run time of all services.
        self.Memory.Save()
        # Deep sleep, this function call does not return (if successful).
        self.DeepSleep.DeepSleep(t_sec * 1000)
        # Raise an exception to stop the scheduler if deep sleep fails.
        print("[Scheduler] Error: Deep sleep failed.")
        raise SchedulerExceptionDeepSleepFailed

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
        sleep_time = 0
        # Activate periodic services.
        for svc in self.Services:
            if svc.SvcMode is Service.MODE_RUN_PERIODIC:
                print("[Scheduler] Updating periodic service: {}".format(svc))
                # If interval time has passed, activate the service.
                if self.RunTimeSec >= svc.SvcInterval + svc.SvcLastRun:
                    print("[Scheduler] Activating periodic service: {}".format(svc))
                    svc.SvcActivate()
                # Otherwise calculate the sleep time based on the interval and last run
                # timestamp.
                else:
                    sleep_time = svc.SvcInterval - (self.RunTimeSec - svc.SvcLastRun)

        return sleep_time

    def _CheckServiceDependencies(self, service):
        ready = True
        for svc_dep in service.SvcDeps:
            print("[Scheduler] Checking dependency: {}".format(svc_dep))
            if svc_dep.SvcLastRun is 0:
                svc_dep.SvcActivate()
                ready = False
        print("[Scheduler] Dependencies ran: {}".format(ready))
        return ready

    def _IndexAdvance(self, svc_activated):
        print("[Scheduler] Service activated: {}".format(svc_activated))
        # Increment the service list index.
        # Wrap around if the end if reached.
        self.Index += 1

        if self.Index >= len(self.Services):
            self.Index = 0
            # A minimum of one service must
            # have been activated.
            return svc_activated

        return True

    def _CyclesDec(self):
        if self.Cycles is not None:
            self.Cycles -= 1
            print("[Scheduler] Cycles left: {}.".format(self.Cycles))
            if self.Cycles is 0:
                raise SchedulerExceptionStopped
