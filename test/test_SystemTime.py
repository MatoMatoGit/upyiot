import sys

sys.path.append('../')

# Test libraries
import unittest

# Unit Under Test
from upyiot.module.SystemTime.SystemTime import SystemTime


class test_SystemTime(unittest.TestCase):

    def setUp(arg):
        return

    def tearDown(arg):
        return

    def test_Constructor(self):
        sys_time = SystemTime.InstanceGet()

        self.assertFalse(sys_time is None)

    def test_Singleton(self):
        sys_time = SystemTime.InstanceGet()
        sys_time1 = SystemTime.InstanceGet()

        self.assertEqual(sys_time, sys_time1)

        except_occurred = False
        try:
            SystemTime.SystemTime()
        except:
            except_occurred = True
        finally:
            self.assertTrue(except_occurred)

    def test_Service(self):
        sys_time = SystemTime.InstanceGet()

        sys_time.SvcRun()

    def test_testNow(self):
        sys_time = SystemTime.InstanceGet()

        sys_time.SvcRun()
        now = sys_time.Now()

        self.assertFalse(now[0] is 0)

    def test_DateTime(self):
        sys_time = SystemTime.InstanceGet()

        sys_time.SvcRun()
        dt = sys_time.DateTime()
        print("Formatted time: {}".format(dt))

        self.assertIn('2019', dt)
        self.assertIn('T', dt)
