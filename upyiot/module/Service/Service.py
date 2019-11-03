from micropython import const


class ServiceException(Exception):

    def __init__(self):
        return


class ServiceExceptionSuspend(ServiceException):

    def __init__(self):
        return


class Service:

    MODE_RUN_ONCE       = const(0)
    MODE_RUN_PERIODIC   = const(1)

    STATE_DISABLED      = const(-2)
    STATE_UNINITIALIZED = const(-1)
    STATE_SUSPENDED     = const(0)
    STATE_READY         = const(1)

    def __init__(self, mode, service_deps, interval=0):
        print("[Service] Dependencies: {}".format(service_deps))
        self.SvcMode = mode
        self.SvcDeps = service_deps
        self.SvcInterval = interval
        self.SvcLastRun = 0
        self.SvcState = Service.STATE_UNINITIALIZED
        self.SvcActive = False

# #### Service base interface ####

    def SvcInit(self):
        pass

    def SvcDeinit(self):
        pass

    def SvcRun(self):
        pass


# #### Service core interface ####

    def SvcIsInitialized(self):
        return self.SvcState is not Service.STATE_UNINITIALIZED

    def SvcIsReady(self):
        return self.SvcState is Service.STATE_READY

    def SvcIsActive(self):
        return self.SvcActive

    def SvcActivate(self):
        self.SvcActive = True

    def SvcDeactivate(self):
        self.SvcActive = False

    def SvcStateGet(self):
        return self.SvcState

    def SvcSuspend(self):
        raise ServiceExceptionSuspend

# #### Service scheduler only ####

    def SvcStateSet(self, state):
        self.SvcState = state
        print("[Service] New state: {}".format(self.SvcState))

    def SvcLastRunSet(self, t):
        self.SvcLastRun = t
        print("[Service] Last run: {}".format(self.SvcLastRun))
