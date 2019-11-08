import sys
sys.path.append('../')

# Test libraries
import unittest

# Unit Under Test
from upyiot.middleware.Singleton import Singleton

# Other


class ConcreteSingleton(Singleton.Singleton):

    def __init__(self):
        self.InstanceSet(self)


class test_Singleton(unittest.TestCase):

    Singleton = None

    def setUp(arg):
        test_Singleton.Singleton = Singleton.Singleton()

    def tearDown(arg):
        return

    def test_Constructor(self):
        self.assertIsNone(self.Singleton.InstanceGet())
        return

    def test_InstanceSetOnce(self):
        sub_class = 3
        self.Singleton.InstanceSet(sub_class)
        self.assertEqual(self.Singleton.InstanceGet(), sub_class)

    def test_InstanceTwice(self):
        sub_class = 3
        self.Singleton.InstanceSet(sub_class)
        exp_raised = False
        try:
            self.Singleton.InstanceSet(sub_class)
        except:
            exp_raise = True
        self.assertTrue(exp_raise)

    def test_ConreteSingleton(self):
        concrete = ConcreteSingleton()
        instance = concrete.InstanceGet()

        self.assertEqual(concrete, instance)

