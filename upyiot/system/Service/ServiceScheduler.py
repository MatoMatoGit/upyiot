import sys
from upyiot.system.Service.Service import Service
from upyiot.system.Service.Service import ServiceExceptionSuspend
from upyiot.system.Service.Service import ServiceException
from upyiot.middleware.StructFile.StructFile import StructFile
from upyiot.system.ExtLogging import ExtLogging

import utime
from micropython import const

Log = ExtLogging.Create("Scheduler")


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
    SVC_NAME_LEN = const(20)
    SVC_MEM_FMT = "<" + str(SVC_NAME_LEN) + "siI"
    SCHED_MEM_FMT = "<III"

    SCHED_MEM_RUNTIME = const(0)
    SCHED_MEM_SLEEPTIME = const(1)
    SCHED_MEM_NUM_SVC = const(2)

    SVC_MEM_NAME = const(0)
    SVC_MEM_LAST_RUN = const(1)
    SVC_MEM_INTERVAL = const(2)

    def __init__(self, directory, scheduler_obj):
        self.Sfile = StructFile(directory + self.FILE_SCHEDULER_MEMORY,
                                self.SVC_MEM_FMT,
                                self.SCHED_MEM_FMT)
        self.Scheduler = scheduler_obj
        self.NumEntries = 0

    def Delete(self):
        self.Sfile.Delete()

    def Save(self):
        # Clear the memory.
        self.Sfile.Clear()

        # Iterate through all registered services and store their data.
        i = 0
        for svc in self.Scheduler.Services:
            Log.debug("Mem: Writing data for service {}".format(svc.SvcName))
            sto_name = svc.SvcName + ((self.SVC_NAME_LEN - len(svc.SvcName)) * "\0")
            self.Sfile.WriteData(i, sto_name, svc.SvcLastRun, svc.SvcInterval)
            i += 1

        self.NumEntries = len(self.Scheduler.Services)
        Log.info("Mem: Saving total number of service entries: {}".format(self.NumEntries))
        # Store the scheduler data (in the StructFile meta).
        Log.debug("Mem: Writing scheduler data")
        self.Sfile.WriteMeta(self.Scheduler.RunTimeSec, self.Scheduler.SleepTime,
                             self.NumEntries)
        return 0

    def Load(self):
        # Load the scheduler data first (from the StructFile meta).
        sched_mem = self.Sfile.ReadMeta()
        if sched_mem is not None:
            self.Scheduler.RunTimeSec = sched_mem[self.SCHED_MEM_RUNTIME]
            self.Scheduler.SleepTime = sched_mem[self.SCHED_MEM_SLEEPTIME]
            self.NumEntries = sched_mem[self.SCHED_MEM_NUM_SVC]
        else:
            return -1

        Log.info("Mem: Read scheduler data. RunTime: {} | SleepTime: {} "
              "| NumServices: {}".format(self.Scheduler.RunTimeSec,
                                         self.Scheduler.SleepTime,
                                         self.NumEntries))

        self.Sfile.IteratorConfig(0, self.NumEntries - 1)

        # Iterate through the set of stored service data and restore
        # the data if a matching service is found (by name).
        for svc_mem in self.Sfile:
            svc_name = svc_mem[self.SVC_MEM_NAME].decode("utf-8").split("\0")[0]
            Log.debug("Mem: Read data for service {}: ".format(svc_name, svc_mem))
            idx = self.Sfile.IteratorIndex()
            if idx < len(self.Scheduler.Services):
                # First service to check if the one at the same index as it was stored at.
                # The chance is very high that the services were registered in the same order.
                svc = self.Scheduler.Services[idx]
                Log.debug("Mem: Same-index service {}".format(svc.SvcName))
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

        Log.info("Mem: Finished loading memory.")
        return 0

    def _LoadService(self, svc, svc_mem):
        if svc is None:
            return
        svc.SvcLastRun = svc_mem[self.SVC_MEM_LAST_RUN]
        svc.SvcInterval = svc_mem[self.SVC_MEM_INTERVAL]

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
        Log.debug("Mem: Searching service: {}".format(name))
        for svc in self.Scheduler.Services:
            if svc.SvcName == name:
                return svc
        return None


class ServiceScheduler:

    SCHEDULER_RESULT_OK     = const(0)
    SCHEDULER_RESULT_ERR    = const(-1)
    MIN_DEEPSLEEP_TIME      = const(10)

    SCHED_STATE_STOPPED = const(0)
    SCHED_STATE_IDLE    = const(1)
    SCHED_STATE_RUNNING = const(2)

    def __init__(self, deepsleep_threshold_sec=MIN_DEEPSLEEP_TIME, deep_sleep_obj=None, directory="./"):
        self.Services = list()
        self.RunTimeSec = 0
        self.Cycles = None
        self.Index = 0
        self.DeepSleepThresholdSec = deepsleep_threshold_sec
        self.DeepSleep = deep_sleep_obj
        self.CbsBeforeDeepSleep = set()
        self.SleepTime = 0
        self.SleepTimeRequested = -1
        self.Memory = SchedulerMemory(directory, self)
        self.State = self.SCHED_STATE_STOPPED

        if self.DeepSleep is None:
            from upyiot.drivers.Sleep.MachineDeepSleep import MachineDeepSleep
            self.DeepSleep = MachineDeepSleep()

        return

    def ServiceRegister(self, service):
        self.Services.append(service)
        Log.debug("Registered service: {}".format(service.SvcName))

        return 0

    def ServiceDeregister(self, service):
        res = 0
        try:
            if service.SvcIsInitialized() is True:
                service.SvcDeinit()
                service.SvcStateSet(Service.STATE_UNINITIALIZED)
                Log.debug("Deregistered service: {}".format(service.SvcName))
        except Exception as e:
            Log.error("Exception occurred while deregistering service {}: {}".format(service.SvcName, e))
            sys.print_exception(e)
            service.SvcStateSet(Service.STATE_DISABLED)
            res = -1
        finally:
            self.Services.remove(service)
        return res

    def Run(self, cycles=None):
        self.State = self.SCHED_STATE_RUNNING

        # Load the scheduler run time, and last-run time of all services.
        self.Memory.Load()

        self.Cycles = cycles

        Log.info("##### Run #####")
        try:
            # Infinite loop
            while True:
                Log.info("\n##### Cycles left: {} #####\n".format(self.Cycles))
                # Add the amount time spend sleeping or idling.
                self._UpdateRuntime(self.SleepTime)

                Log.info("Run time (s): {}".format(self.RunTimeSec))

                # Service run loop.
                # Runs a service until none are ready or have been activated.
                self.Index = 0
                while True:
                    # Save the start time before executing the loop.
                    t_start = utime.ticks_ms()

                    svc_activated = False

                    if self.Index >= len(self.Services):
                        Log.debug("No services registered")
                        t_ran_sec = self._CalculateRuntime(t_start)
                        self._UpdateRuntime(t_ran_sec)
                        # Decrease the amount of scheduler cycles left (if applicable).
                        self._CyclesDec()
                        break

                    # Update all periodic services.
                    self.SleepTime = self._UpdatePeriodicServices()
                    Log.debug("Shortest sleep time: {}".format(self.SleepTime))

                    service = self.Services[self.Index]

                    if service.SvcStateGet() is not service.STATE_DISABLED:
                        Log.debug("Checking: {}".format(service.SvcName))

                        # If the service has been activated.
                        if service.SvcIsActive() is True:

                            # If the service has not been initialized, initialize
                            # it.
                            if service.SvcIsInitialized() is False:
                                res = self._InitializeService(service)

                                # If the result is 1 the service cannot be initialized yet
                                # due to a dependency. The dependency has been activated.
                                if res is 1:
                                    svc_activated = True

                            if service.SvcIsInitialized() is True:

                                # Check if all run dependencies are okay.
                                # If this is the case the service is ready
                                # to run.
                                if self._CheckServiceDependencies(service) is False:
                                    # If the service dependency check returns False, it means
                                    # there is at least one service that has been activated.
                                    svc_activated = True
                                else:
                                    Log.debug("Ready: {}".format(service.SvcName))
                                    service.SvcStateSet(Service.STATE_READY)

                        # If the service is ready to run, run it.
                        if service.SvcIsReady() is True:
                            Log.info("Running: {}".format(service.SvcName))
                            svc_activated = True
                            self._ServiceRun(service)
                    else:
                        Log.info("Disabled: {}".format(service.SvcName))

                    t_ran_sec = self._CalculateRuntime(t_start)
                    self._UpdateRuntime(t_ran_sec)

                    # Decrease the amount of scheduler cycles left (if applicable).
                    self._CyclesDec()

                    Log.debug("Selecting next service")
                    # if self._IndexAdvance(svc_activated) is False:
                    #     print("[Scheduler] No more services to run")
                    #     break
                    self._IndexAdvance(svc_activated)
                    if self._CheckServiceActive() is False and svc_activated is False:
                        Log.debug("No more services to run")
                        break

                    Log.debug("Next index: {}".format(self.Index))

                # The statements below run after the scheduler finishes checking
                # the services that are ready / have been activated.

                if self.SleepTimeRequested is not -1:
                    Log.info("Initiating requested deep sleep for {} seconds".format(self.SleepTimeRequested))
                    self._InitiateDeepSleep(self.SleepTimeRequested)

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
                elif self.SleepTime < self.DeepSleepThresholdSec:
                    Log.info("Idling for {} seconds".format(self.SleepTime))
                    # No services are ready at this moment.
                    utime.sleep(self.SleepTime)
                    self.State = self.SCHED_STATE_IDLE

                # If the shortest sleep time is sufficient for a deepsleep,
                # initiate it.
                else:
                    Log.info("Initiating deep sleep for {} seconds".format(self.SleepTime))
                    self._InitiateDeepSleep(self.SleepTime)

        except SchedulerExceptionStopped:
            self.State = self.SCHED_STATE_STOPPED
            Log.info("Stopped.")

    def RequestDeepSleep(self, t_sec):
        if self.State is self.SCHED_STATE_STOPPED:
            self._InitiateDeepSleep(t_sec)
        else:
            self.SleepTimeRequested = t_sec
            return 0

    def RegisterCallbackBeforeDeepSleep(self, callback):
        self.CbsBeforeDeepSleep.add(callback)

    def _NotifyBeforeDeepSleep(self):
        for cb in self.CbsBeforeDeepSleep:
            cb()

    def _CalculateRuntime(self, t_start):
        # Calculate the amount of time that passed while running services.
        t_end = utime.ticks_ms()
        t_ran = utime.ticks_diff(t_end, t_start)
        t_ran_sec = int(round((t_ran / 1000)))

        Log.debug("t start: {}  | "
                  "t_end: {} | t_ran (ms): {} | "
                  "t ran (s): {}".format(t_start,
                                         t_end,
                                         t_ran,
                                         t_ran_sec))

        return t_ran_sec

    def _UpdateRuntime(self, t_sec):
        # Add the amount time that passed since the last update.
        self.RunTimeSec += t_sec

    def _InitiateDeepSleep(self, t_sec):
        # Call registered BeforeDeepSleep callbacks.
        self._NotifyBeforeDeepSleep()
        # Save the scheduler run time, and last-run time of all services.
        self.Memory.Save()
        # Deep sleep, this function call does not return (if successful).
        self.DeepSleep.DeepSleep(t_sec * 1000)
        # Raise an exception to stop the scheduler if deep sleep fails.
        Log.error("Deep sleep failed.")
        raise SchedulerExceptionDeepSleepFailed

    def _ServiceRun(self, service):
        try:
            service.SvcRun()
            service.SvcStateSet(Service.STATE_SUSPENDED)
        except ServiceExceptionSuspend:
            Log.info("Suspending service")
            service.SvcStateSet(Service.STATE_SUSPENDED)
        except ServiceException:
            Log.error("Error occurred, disabling service.")
            service.SvcStateSet(Service.STATE_DISABLED)
        except Exception as e:
            sys.print_exception(e)

        if service.SvcState is not Service.STATE_DISABLED:
            # Update the last run timestamp.
            service.SvcLastRunSet(self.RunTimeSec)
            service.SvcDeactivate()
            service.SvcRunCount += 1

    def _InitializeService(self, service):
        try:
            if self._CheckServiceDependencies(service) is True:
                service.SvcInit()
                service.SvcStateSet(Service.STATE_SUSPENDED)
                res = 0
            else:
                res = 1
        except Exception as e:
            Log.error("Exception occurred while initializing service {}: {}".format(service.SvcName, e))
            sys.print_exception(e)
            service.SvcStateSet(Service.STATE_DISABLED)
            res = -1

        return res

    def _UpdatePeriodicServices(self):
        shortest_sleep_time = 0
        # Activate periodic services.
        for svc in self.Services:
            if svc.SvcMode is Service.MODE_RUN_PERIODIC and svc.SvcState is not Service.STATE_DISABLED:
                if svc.SvcLastRun is -1:
                    last_run = 0
                else:
                    last_run = svc.SvcLastRun
                Log.debug("Updating periodic service: {}".format(svc.SvcName))
                # If interval time has passed, activate the service.
                if self.RunTimeSec >= svc.SvcInterval + last_run:
                    Log.debug("Activating periodic service: {}".format(svc.SvcName))
                    svc.SvcActivate()
                # Otherwise calculate the sleep time based on the interval and last run
                # timestamp.
                else:
                    sleep_time = svc.SvcInterval - (self.RunTimeSec - last_run)
                    if shortest_sleep_time is 0 or sleep_time < shortest_sleep_time:
                        shortest_sleep_time = sleep_time

        return shortest_sleep_time

    def _CheckServiceDependencies(self, service):
        ready = True
        # Iterator through the dependency dict keys.
        for svc_dep in service.SvcDeps.keys():
            Log.debug("Checking dependency: {}".format(svc_dep.SvcName))

            # Check if the service was initialized
            if service.SvcState is Service.STATE_UNINITIALIZED:

                # The service dependency must have run before the dependent
                # service is initialized.
                if service.SvcDeps[svc_dep] is Service.DEP_TYPE_RUN_ONCE_BEFORE_INIT:
                    if svc_dep.SvcLastRun is -1:
                        self._ActivateFromDependency(svc_dep)
                        ready = False

                elif service.SvcDeps[svc_dep] is Service.DEP_TYPE_RUN_ALWAYS_BEFORE_INIT:
                    if svc_dep.SvcRunCount is 0:
                        self._ActivateFromDependency(svc_dep)
                        ready = False

            # The service dependency must have run before the dependent
            # service is ran.
            else:
                # The service dependency must have run before the dependent
                # service is initialized.
                if service.SvcDeps[svc_dep] is Service.DEP_TYPE_RUN_ONCE_BEFORE_RUN:
                    if svc_dep.SvcLastRun is -1:
                        self._ActivateFromDependency(svc_dep)
                        ready = False

                elif service.SvcDeps[svc_dep] is Service.DEP_TYPE_RUN_ALWAYS_BEFORE_RUN:
                    if svc_dep.SvcRunCount is 0:
                        self._ActivateFromDependency(svc_dep)
                        ready = False

        Log.debug("Dependencies ok: {}".format(ready))
        return ready

    def _ActivateFromDependency(self, service):
        # The service dependency must NOT be disabled, otherwise
        # the dependency cannot be activated.
        if service.SvcState is not Service.STATE_DISABLED:
            Log.debug("Activating dependency: {}".format(service.SvcName))
            service.SvcActivate()
            return 0
        else:
            Log.debug("Dependency {} is disabled".format(service.SvcName))
            return -1

    def _IndexAdvance(self, svc_activated):
        # Increment the service list index.
        # Wrap around if the end if reached.
        self.Index += 1

        if self.Index >= len(self.Services):
            Log.debug("Resetting service list index")
            self.Index = 0
            # A minimum of one service must
            # have been activated.
            return svc_activated

        return True

    def _CyclesDec(self):
        if self.Cycles is not None:
            self.Cycles -= 1
            Log.debug("Cycles left: {}.".format(self.Cycles))
            if self.Cycles is 0:
                raise SchedulerExceptionStopped

    def _CheckServiceActive(self):
        for svc in self.Services:
            if svc.SvcIsActive():
                return True
        return False
