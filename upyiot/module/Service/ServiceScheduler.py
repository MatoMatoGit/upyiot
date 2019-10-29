from module.Service.Service import Service
import utime


class ServiceScheduler:

    def __init__(self):
        self.Services = list()
        self.Ticks = 0
        return

    def ServiceRegister(self, service):
        self.Services.append(service)
        return

    def ServiceDeregister(self, service):
        self.Services.remove(service)
        return

    def Run(self, start_service):
        exe_service = start_service
        exe_service.Activate()

        # Infinite loop
        while True:
            self.Ticks += 1

            # Service run loop.
            # Runs a service until none are ready.
            while True:
                try:
                    if exe_service.IsInitialized() is False:
                        exe_service.Init()
                        exe_service.StateSet(Service.STATE_SUSPENDED)
                except:
                    exe_service.StateSet(Service.STATE_DISABLED)

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
