from module.Service.Service import Service
import utime


class ServiceScheduler:

    def __init__(self):
        self.Services = list()
        self.Ticks = 0
        return

    def ServiceRegister(self, service):
        res = 0
        try:
            if service.IsInitialized() is False:
                service.Init()
                service.StateSet(Service.STATE_SUSPENDED)
                self.Services.append(service)
        except:
            service.StateSet(Service.STATE_DISABLED)
            res = -1

        return res

    def ServiceDeregister(self, service):
        res = 0
        try:
            if service.IsInitialized() is True:
                service.Deinit()
                service.StateSet(Service.STATE_UNINITIALIZED)
        except:
            service.StateSet(Service.STATE_DISABLED)
            res = -1
        finally:
            self.Services.remove(service)
        return res

    def Run(self, cycles=None):

        # Infinite loop
        while True:
            self.Ticks += 1

            # Activate periodic services.
            for svc in self.Services:
                if svc.Mode is Service.MODE_RUN_PERIODIC:
                    # If interval time has passed, activate the service.
                    if self.Ticks + svc.LastRun >= svc.Interval:
                        svc.Activate()

            # Service run loop.
            # Runs a service until none are ready.
            index = 0
            svc_ran = False
            while True:
                if index >= len(self.Services):
                    break

                service = self.Services[index]

                # Check if all services that this service is dependent on
                # ran at least once. If this is the case the service is ready
                # to run.
                if service.IsActive() and self._CheckServiceDependencies(service) is True:
                    service.StateSet(Service.STATE_READY)

                # If the service is ready to run, call its Run method.
                if service.IsReady() is True:
                    svc_ran = True
                    service.Deactivate()
                    try:
                        service.Run()
                        service.StateSet(Service.STATE_SUSPENDED)
                        # Update the last run timestamp.
                        service.LastRun(self.Ticks)
                    except:
                        service.StateSet(Service.STATE_DISABLED)

                # Increment the service list index.
                # Wrap around if the end if reached.
                index += 1
                if index >= len(self.Services):
                    index = 0
                    # A minimum of one service must
                    # have ran.
                    if svc_ran is False:
                        break
                    svc_ran = False

            # No services are ready at this moment.
            utime.sleep(1)

            if cycles is not None:
                cycles -= 1
                if cycles is 0:
                    break

    def _CheckServiceDependencies(self, service):
        ready = True
        for svc_dep in service.ServiceDeps:
            if svc_dep.LastRun() is 0:
                svc_dep.Schedule()
                ready = False

        return ready
