import sys
sys.path.append('../upyiot/')

# Test libraries
import unittest
from StubFunction import StubFunction
from TestUtil import TestUtil

# Unit Under Test
from module.Service.ServiceScheduler import ServiceScheduler
from module.Service.Service import Service

# Other


class TestService(Service):

    def __init__(self, mode, service_deps, interval=0):
        super().__init__(mode, service_deps, interval)
        self.ErrInit = False
        self.ErrDeinit = False
        self.ErrRun = False
        self.Init = StubFunction()
        self.Deinit = StubFunction()
        self.Run = StubFunction()


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
        self.assertEqual(svc.StateGet(), Service.STATE_SUSPENDED)
        self.assertEqual(len(self.Scheduler.Services), 1)

    def test_ServiceRegisterException(self):
        svc = TestService(Service.MODE_RUN_ONCE, ())
        svc.Init.SetRaiseExc()

        res = self.Scheduler.ServiceRegister(svc)

        self.assertEqual(res, -1)
        self.assertEqual(svc.StateGet(), Service.STATE_DISABLED)


    def test_ServiceDeregisterSuccessful(self):
        svc = TestService(Service.MODE_RUN_ONCE, ())

        self.Scheduler.ServiceRegister(svc)
        res = self.Scheduler.ServiceDeregister(svc)

        self.assertEqual(res, 0)
        self.assertEqual(svc.StateGet(), Service.STATE_UNINITIALIZED)
        self.assertEqual(len(self.Scheduler.Services), 0)


    def test_ServiceDeregisterException(self):
        svc = TestService(Service.MODE_RUN_ONCE, ())

        self.Scheduler.ServiceRegister(svc)
        svc.Deinit.SetRaiseExc()
        res = self.Scheduler.ServiceDeregister(svc)

        self.assertEqual(res, -1)
        self.assertEqual(svc.StateGet(), Service.STATE_DISABLED)

    def test_RunOnceNoServices(self):
        self.Scheduler.Run(1)

        return

