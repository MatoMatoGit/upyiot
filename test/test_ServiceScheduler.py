import sys
sys.path.append('../')

# Test libraries
import unittest
from StubFunction import StubFunction
from TestUtil import TestUtil

# Unit Under Test
from upyiot.system.Service.ServiceScheduler import ServiceScheduler

# Other
from upyiot.system.Service.Service import Service
from upyiot.system.Service.Service import ServiceException
from upyiot.system.Service.Service import ServiceExceptionSuspend


class TestService(Service):

    def __init__(self, mode, service_deps, interval=0, run_func=None):
        super().__init__(mode, service_deps, interval)

        # Create  methods
        self.SvcInit = StubFunction()
        self.SvcDeinit = StubFunction()
        self.SvcRun = StubFunction(func=run_func, exc=ServiceException)


class test_ServiceScheduler(unittest.TestCase):

    def setUp(self):
        self.Scheduler = ServiceScheduler()
        return

    def tearDown(self):
        return

    def test_ServiceRegisterSuccessful(self):
        svc = TestService(Service.MODE_RUN_ONCE, ())

        res = self.Scheduler.ServiceRegister(svc)

        self.assertEqual(res, 0)
        self.assertEqual(svc.SvcInit.CallCount, 1)
        self.assertEqual(svc.SvcStateGet(), Service.STATE_SUSPENDED)
        self.assertEqual(len(self.Scheduler.Services), 1)

    def test_ServiceRegisterException(self):
        svc = TestService(Service.MODE_RUN_ONCE, ())
        svc.SvcInit.RaiseExcSet()

        res = self.Scheduler.ServiceRegister(svc)

        self.assertEqual(res, -1)
        self.assertEqual(svc.SvcStateGet(), Service.STATE_DISABLED)

    def test_ServiceDeregisterSuccessful(self):
        svc = TestService(Service.MODE_RUN_ONCE, ())

        self.Scheduler.ServiceRegister(svc)
        res = self.Scheduler.ServiceDeregister(svc)

        self.assertEqual(res, 0)
        self.assertEqual(svc.SvcStateGet(), Service.STATE_UNINITIALIZED)
        self.assertEqual(svc.SvcDeinit.CallCount, 1)
        self.assertEqual(len(self.Scheduler.Services), 0)

    def test_ServiceDeregisterException(self):
        svc = TestService(Service.MODE_RUN_ONCE, ())

        self.Scheduler.ServiceRegister(svc)
        svc.SvcDeinit.RaiseExcSet()
        res = self.Scheduler.ServiceDeregister(svc)

        self.assertEqual(res, -1)
        self.assertEqual(svc.SvcStateGet(), Service.STATE_DISABLED)

    def test_RunOnceNoServices(self):
        self.Scheduler.Run(1)

    @staticmethod
    def PeriodicServiceRun(stub_func_obj):
        print("[PeriodicService] Called")

    @staticmethod
    def OneShotServiceRun(stub_func_obj):
        print("[OneShotService] Called")

    def test_RunServicePeriodic(self):
        run_count = 2
        interval = 2
        svc = TestService(Service.MODE_RUN_PERIODIC, (), interval, test_ServiceScheduler.PeriodicServiceRun)
        self.Scheduler.ServiceRegister(svc)

        self.Scheduler.Run(interval * run_count)

        self.assertEqual(svc.SvcRun.CallCount, run_count)

    def test_RunServiceOnce(self):
        svc = TestService(Service.MODE_RUN_ONCE, (), run_func=test_ServiceScheduler.PeriodicServiceRun)
        self.Scheduler.ServiceRegister(svc)

        svc.SvcActivate()
        self.Scheduler.Run(2)

        self.assertEqual(svc.SvcRun.CallCount, 1)

    def test_RunServiceMixed(self):
        svc_periodic = TestService(Service.MODE_RUN_PERIODIC, (), 2, test_ServiceScheduler.PeriodicServiceRun)
        svc_once = TestService(Service.MODE_RUN_ONCE, (), run_func=test_ServiceScheduler.OneShotServiceRun)

        self.Scheduler.ServiceRegister(svc_periodic)
        self.Scheduler.ServiceRegister(svc_once)
        svc_once.SvcActivate()
        self.Scheduler.Run(3)

        self.assertEqual(svc_once.SvcRun.CallCount, 1)
        self.assertEqual(svc_periodic.SvcRun.CallCount, 1)

    def test_RunServiceFromDependency(self):
        svc_once = TestService(Service.MODE_RUN_ONCE, (), run_func=test_ServiceScheduler.OneShotServiceRun)
        svc_deps = (svc_once, )
        svc_periodic = TestService(Service.MODE_RUN_PERIODIC, svc_deps, 2, test_ServiceScheduler.PeriodicServiceRun)

        self.Scheduler.ServiceRegister(svc_periodic)
        self.Scheduler.ServiceRegister(svc_once)
        self.Scheduler.Run(3)

        self.assertEqual(svc_once.SvcRun.CallCount, 1)
        self.assertEqual(svc_periodic.SvcRun.CallCount, 1)

    def test_RunDisableServiceOnException(self):
        svc = TestService(Service.MODE_RUN_PERIODIC, (), 2, test_ServiceScheduler.PeriodicServiceRun)
        self.Scheduler.ServiceRegister(svc)
        print(svc)

        svc.SvcRun.RaiseExcSet()
        self.Scheduler.Run(3)

        self.assertEqual(svc.SvcStateGet(), Service.STATE_DISABLED)

    def test_RunServiceSuspend(self):
        svc = TestService(Service.MODE_RUN_PERIODIC, (), 2, test_ServiceScheduler.PeriodicServiceRun)
        self.Scheduler.ServiceRegister(svc)
        print(svc)

        svc.SvcRun.Exc = ServiceExceptionSuspend
        svc.SvcRun.RaiseExcSet()
        self.Scheduler.Run(3)

        self.assertEqual(svc.SvcStateGet(), Service.STATE_SUSPENDED)
