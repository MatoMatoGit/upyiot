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

    DEP_TYPE_RUN_ONCE_BEFORE_INIT   = const(0)
    DEP_TYPE_RUN_ONCE_BEFORE_RUN    = const(1)
    DEP_TYPE_RUN_ALWAYS_BEFORE_INIT = const(2)
    DEP_TYPE_RUN_ALWAYS_BEFORE_RUN  = const(3)

    STATE_DISABLED      = const(-2)
    STATE_UNINITIALIZED = const(-1)
    STATE_SUSPENDED     = const(0)
    STATE_READY         = const(1)

    def __init__(self, name, mode, service_deps, interval=0):
        """

        :param name:
        :param mode:
        :param service_deps: Dictionary containing a dependency type value for each
        service key.
        :param interval:
        """
        self.SvcName = name
        self.SvcMode = mode
        self.SvcDeps = service_deps
        self.SvcInterval = interval
        self.SvcLastRun = -1
        self.SvcState = Service.STATE_UNINITIALIZED
        self.SvcActive = False
        self.SvcRunCount = 0
        print("[Service] Dependencies: {}".format(self.SvcDeps))

# #### Service base API ####

    def SvcInit(self):
        pass

    def SvcDeinit(self):
        pass

    def SvcRun(self):
        pass

# #### Service core API ####

    def SvcNameSet(self, name):
        self.SvcName = name

    def SvcDependencies(self, svc_deps):
        self.SvcDeps = svc_deps
        print("[Service] Dependencies: {}".format(self.SvcDeps))

    def SvcIntervalSet(self, interval):
        self.SvcInterval = interval

    def SvcIsInitialized(self):
        return self.SvcState is not Service.STATE_UNINITIALIZED

    def SvcIsReady(self):
        return self.SvcState is Service.STATE_READY

    def SvcIsActive(self):
        return self.SvcActive

    def SvcActivate(self):
        if self.SvcState is not Service.STATE_DISABLED:
            self.SvcActive = True

    def SvcDeactivate(self):
        self.SvcActive = False

    def SvcStateGet(self):
        return self.SvcState

    def SvcSuspend(self):
        raise ServiceExceptionSuspend

    def SvcStateString(self, state):
        if state is self.STATE_DISABLED:
            return "Disabled"
        elif state is self.STATE_UNINITIALIZED:
            return "Uninitialized"
        elif state is self.STATE_SUSPENDED:
            return "Suspended"
        else:
            return "Ready"

# #### Service Scheduler only ####

    def SvcStateSet(self, state):
        self.SvcState = state
        print("[Service] New state: {}".format(self.SvcStateString(self.SvcState)))

    def SvcLastRunSet(self, t):
        self.SvcLastRun = t
        print("[Service] Last run: {}".format(self.SvcLastRun))
