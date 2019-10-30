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
                self.Services.remove(service)
        except:
            service.StateSet(Service.STATE_DISABLED)
            res = -1

        return res

    def Run(self, start_service):
        start_service.Activate()

        # Infinite loop
        while True:
            self.Ticks += 1

            # Service run loop.
            # Runs a service until none are ready.
            while True:
                # Handle periodic services.
                if exe_service.Mode is Service.MODE_RUN_PERIODIC:
                    # If interval time has passed, activate the service.
                    if self.Ticks + exe_service.LastRun >= exe_service.Interval:
                        exe_service.Activate()

                # Check if all services that this service is dependent on
                # ran at least once.
                if self._CheckServiceDependencies(exe_service) is True:
                    exe_service.StateSet(Service.STATE_READY)

                if exe_service.IsReady() is True:

                    try:
                        exe_service.Run()
                        exe_service.StateSet(Service.STATE_SUSPENDED)
                        exe_service.LastRun(self.Ticks)
                        exe_service = None
                    except:
                        exe_service.StateSet(Service.STATE_DISABLED)


            # No services are ready at this moment.
            utime.sleep(1)

        return

    def _CheckServiceDependencies(self, service):
        ready = True
        for svc_dep in service.ServiceDeps:
            if svc_dep.LastRun() is 0:
                svc_dep.Schedule()
                ready = False

        return ready
