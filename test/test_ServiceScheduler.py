import sys
sys.path.append('../')

# Test libraries
import unittest
from StubFunction import StubFunction
from stubs import machine

# Unit Under Test
from upyiot.system.Service.ServiceScheduler import ServiceScheduler

# Other
from upyiot.system.Service.Service import Service
from upyiot.system.Service.Service import ServiceException
from upyiot.system.Service.Service import ServiceExceptionSuspend
from upyiot.drivers.Sleep.DeepSleep import DeepSleepExceptionInitiated

import utime


class TestService(Service):
    TEST_SERVICE_DURATION = 1

    InstanceCount = 0

    def __init__(self, mode, service_deps, interval=0, run_func=None, name=None):
        if name is None:
            name = "tstsvc_" + str(self.InstanceCount)
        super().__init__(name,
                         mode, service_deps, interval)
        TestService.InstanceCount += 1

        # Create  methods
        self.SvcInit = StubFunction()
        self.SvcDeinit = StubFunction()
        self.SvcRun = StubFunction(func=run_func, exc=ServiceException)


class test_ServiceScheduler(unittest.TestCase):

    def setUp(self):
        self.Scheduler = ServiceScheduler()
        return

    def tearDown(self):
        self.Scheduler.Memory.Sfile.Delete()
        return

    # def test_ServiceRegisterAndInitializeSuccessful(self):
    #     svc = TestService(Service.MODE_RUN_ONCE, {})
    #
    #     res = self.Scheduler.ServiceRegister(svc)
    #
    #     self.assertEqual(res, 0)
    #     self.assertEqual(svc.SvcInit.CallCount, 1)
    #     self.assertEqual(svc.SvcStateGet(), Service.STATE_SUSPENDED)
    #     self.assertEqual(len(self.Scheduler.Services), 1)
    #
    # def test_ServiceRegisterNoInitDueToDependency(self):
    #     svc_dep = TestService(Service.MODE_RUN_ONCE, {})
    #     svc = TestService(Service.MODE_RUN_ONCE, {svc_dep: Service.DEP_TYPE_RUN_ONCE_BEFORE_INIT})
    #
    #     res = self.Scheduler.ServiceRegister(svc_dep)
    #     self.assertEqual(res, 0)
    #
    #     res = self.Scheduler.ServiceRegister(svc)
    #
    #     self.assertEqual(res, 0)
    #     self.assertEqual(svc.SvcInit.CallCount, 0)
    #     self.assertEqual(svc.SvcStateGet(), Service.STATE_UNINITIALIZED)
    #     self.assertEqual(svc_dep.SvcStateGet(), Service.STATE_SUSPENDED)
    #     self.assertEqual(len(self.Scheduler.Services), 2)

    # def test_ServiceRegisterException(self):
    #     svc = TestService(Service.MODE_RUN_ONCE, {})
    #     svc.SvcInit.RaiseExcSet()
    #
    #     res = self.Scheduler.ServiceRegister(svc)
    #
    #     self.assertEqual(res, -1)
    #     self.assertEqual(svc.SvcStateGet(), Service.STATE_DISABLED)

    def test_ServiceDeregisterSuccessful(self):
        svc = TestService(Service.MODE_RUN_ONCE, {})

        self.Scheduler.ServiceRegister(svc)
        svc.SvcStateSet(Service.STATE_SUSPENDED)
        res = self.Scheduler.ServiceDeregister(svc)

        self.assertEqual(res, 0)
        self.assertEqual(svc.SvcStateGet(), Service.STATE_UNINITIALIZED)
        self.assertEqual(svc.SvcDeinit.CallCount, 1)
        self.assertEqual(len(self.Scheduler.Services), 0)

    def test_ServiceDeregisterException(self):
        svc = TestService(Service.MODE_RUN_ONCE, {})

        self.Scheduler.ServiceRegister(svc)
        svc.SvcDeinit.RaiseExcSet()
        svc.SvcStateSet(Service.STATE_SUSPENDED)
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
        utime.sleep(TestService.TEST_SERVICE_DURATION)

    def test_RunServicePeriodic(self):
        run_count = 2
        interval = 2
        svc = TestService(Service.MODE_RUN_PERIODIC, {}, interval, test_ServiceScheduler.PeriodicServiceRun)
        self.Scheduler.ServiceRegister(svc)

        self.Scheduler.Run(run_count * 2)

        self.assertEqual(svc.SvcRun.CallCount, run_count)

    def test_RunServiceOnce(self):
        svc = TestService(Service.MODE_RUN_ONCE, {}, run_func=test_ServiceScheduler.PeriodicServiceRun)
        self.Scheduler.ServiceRegister(svc)

        svc.SvcActivate()
        self.Scheduler.Run(1)

        self.assertEqual(svc.SvcRun.CallCount, 1)

    def test_RunServiceMixed(self):
        svc_periodic = TestService(Service.MODE_RUN_PERIODIC, {}, 2, test_ServiceScheduler.PeriodicServiceRun)
        svc_once = TestService(Service.MODE_RUN_ONCE, {}, run_func=test_ServiceScheduler.OneShotServiceRun)

        self.Scheduler.ServiceRegister(svc_periodic)
        self.Scheduler.ServiceRegister(svc_once)
        svc_once.SvcActivate()
        self.Scheduler.Run(4)

        self.assertEqual(svc_once.SvcRun.CallCount, 1)
        self.assertEqual(svc_periodic.SvcRun.CallCount, 1)

    def test_RunServiceFromRunDependency(self):
        svc_once = TestService(Service.MODE_RUN_ONCE, {}, run_func=test_ServiceScheduler.OneShotServiceRun)
        svc_deps = {svc_once: Service.DEP_TYPE_RUN_ALWAYS_BEFORE_RUN}
        svc_periodic = TestService(Service.MODE_RUN_PERIODIC, svc_deps, 2, test_ServiceScheduler.PeriodicServiceRun)

        self.Scheduler.ServiceRegister(svc_periodic)
        self.Scheduler.ServiceRegister(svc_once)
        self.Scheduler.Run(4)

        self.assertEqual(svc_once.SvcRun.CallCount, 1)
        self.assertEqual(svc_periodic.SvcRun.CallCount, 1)

    def test_RunServiceFromInitDependency(self):
        svc_once = TestService(Service.MODE_RUN_ONCE, {}, run_func=test_ServiceScheduler.OneShotServiceRun)
        svc_deps = {svc_once: Service.DEP_TYPE_RUN_ALWAYS_BEFORE_INIT}
        svc_periodic = TestService(Service.MODE_RUN_PERIODIC, svc_deps, 2, test_ServiceScheduler.PeriodicServiceRun)

        self.Scheduler.ServiceRegister(svc_periodic)
        self.Scheduler.ServiceRegister(svc_once)

        self.assertFalse(svc_periodic.SvcIsInitialized())

        self.Scheduler.Run(4)

        self.assertEqual(svc_once.SvcRun.CallCount, 1)
        self.assertEqual(svc_periodic.SvcRun.CallCount, 1)
        self.assertTrue(svc_periodic.SvcIsInitialized())

    def test_RunDisableServiceOnException(self):
        svc = TestService(Service.MODE_RUN_PERIODIC, {}, 2, test_ServiceScheduler.PeriodicServiceRun)
        self.Scheduler.ServiceRegister(svc)
        print(svc)

        svc.SvcRun.RaiseExcSet()
        self.Scheduler.Run(3)

        self.assertEqual(svc.SvcStateGet(), Service.STATE_DISABLED)

    def test_RunServiceSuspend(self):
        svc = TestService(Service.MODE_RUN_PERIODIC, {}, 2, test_ServiceScheduler.PeriodicServiceRun)
        self.Scheduler.ServiceRegister(svc)
        print(svc)

        svc.SvcRun.Exc = ServiceExceptionSuspend
        svc.SvcRun.RaiseExcSet()
        self.Scheduler.Run(3)

        self.assertEqual(svc.SvcStateGet(), Service.STATE_SUSPENDED)

    def test_RunServiceLongDuration(self):
        svc = TestService(Service.MODE_RUN_ONCE, {}, run_func=test_ServiceScheduler.OneShotServiceRun)

        self.Scheduler.ServiceRegister(svc)

        svc.SvcActivate()
        self.Scheduler.Run(1)

        self.assertEqual(svc.SvcRun.CallCount, 1)
        self.assertEqual(self.Scheduler.RunTimeSec, TestService.TEST_SERVICE_DURATION)

    def test_RunServiceAndDeepSleep(self):
        svc = TestService(Service.MODE_RUN_PERIODIC, {}, 20, test_ServiceScheduler.PeriodicServiceRun)

        self.Scheduler.ServiceRegister(svc)

        svc.SvcActivate()

        exc_occurred = False
        try:
            self.Scheduler.Run()
        except DeepSleepExceptionInitiated:
            exc_occurred = True

        self.assertTrue(exc_occurred)
        self.assertEqual(svc.SvcRun.CallCount, 1)
        self.assertEqual(svc.SvcInterval * 1000, machine.asleep_for())

    def test_WakeFromDeepSleepAndRunService(self):
        svc = TestService(Service.MODE_RUN_PERIODIC, {}, 20, test_ServiceScheduler.PeriodicServiceRun)
        svc_name = svc.SvcName

        self.Scheduler.ServiceRegister(svc)

        svc.SvcActivate()

        exc_occurred = False
        try:
            self.Scheduler.Run()
        except DeepSleepExceptionInitiated:
            exc_occurred = True

        self.assertTrue(exc_occurred)
        self.assertTrue(machine.is_asleep())

        new_svc = TestService(Service.MODE_RUN_PERIODIC, {}, 20,
                              test_ServiceScheduler.PeriodicServiceRun,
                              svc_name)

        new_sched = ServiceScheduler()

        new_sched.ServiceRegister(new_svc)

        exc_occurred = False
        try:
            new_sched.Run()
        except DeepSleepExceptionInitiated:
            exc_occurred = True

        self.assertTrue(exc_occurred)

        self.assertEqual(new_svc.SvcRun.CallCount, 1)
        self.assertTrue(machine.is_asleep())
