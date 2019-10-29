from micropython import const


class Service:

    MODE_RUN_ONCE       = const(0)
    MODE_RUN_PERIODIC   = const(1)

    STATE_DISABLED      = const(-2)
    STATE_UNINITIALIZED = const(-1)
    STATE_SUSPENDED     = const(0)
    STATE_READY         = const(1)

    def __init__(self, mode, name, service_deps, interval=0):
        self.Mode = mode
        self.Name = name
        self.ServiceDeps = service_deps
        self.Interval = interval
        self.LastRun = 0
        self.State = Service.STATE_UNINITIALIZED
        self.Activated = False

# #### Service base interface ####

    def Init(self, *args):
        pass

    def Deinit(self):
        pass

    def Run(self, *args):
        pass


# #### Service core interface ####

    def IsInitialized(self):
        return self.State is not Service.STATE_UNINITIALIZED

    def IsReady(self):
        return self.State is Service.STATE_READY

    def IsActive(self):
        return self.Activated

    def Activate(self):
        self.Activated = True

    def StateGet(self):
        return self.State

# #### Service scheduler only ####

    def StateSet(self, state):
        self.State = state

    def LastRun(self, t=None):
        if t is None:
            return self.LastRun
        self.LastRun = t

