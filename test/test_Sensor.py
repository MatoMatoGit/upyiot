import sys
sys.path.append('../')

# Test libraries
import unittest
from stubs import TestObserver
from stubs import DummySensor

# Unit Under Test
from upyiot.middleware.Sensor import Sensor

# Other
from upyiot.middleware.AvgFilter import AvgFilter


class test_Sensor(unittest.TestCase):

    TestDir = "./"
    Name = "dummy"
    Sensor = None
    Samples = [20, 21, 25, 30, 35, 35, 20, 12, 10, 40]

    def setUp(arg):
        filter_depth = len(test_Sensor.Samples)
        dummy = DummySensor.DummySensor(test_Sensor.Samples)
        test_Sensor.Sensor = Sensor.Sensor(test_Sensor.TestDir,
                                           test_Sensor.Name,
                                           filter_depth, dummy)
        test_Sensor.Filter = AvgFilter.AvgFilter(filter_depth)
        return

    def tearDown(arg):
        test_Sensor.Sensor.SamplesDelete()
        return

    def test_Read(self):
        sample = self.Sensor.Read()

        self.assertEqual(sample, self.Samples[0])

    def test_NewSampleObserver(self):
        sample_observer = TestObserver.TestObserver()

        self.Sensor.ObserverAttachNewSample(sample_observer)
        sample = self.Sensor.Read()

        self.assertEqual(sample_observer.State, sample)

    def test_SamplesGet(self):
        filtered = bytearray(len(self.Samples))
        i = 0
        for v in self.Samples:
            self.Filter.Input(v)
            filtered[i] = self.Filter.Output()
            sample = self.Sensor.Read()
            self.assertEqual(filtered[i], sample)
            i = i + 1

        buf = bytearray(self.Sensor.SamplesCount)
        self.Sensor.SamplesGet(buf)

        i = 0
        for i in range(0, len(self.Samples)):
            self.assertEqual(filtered[i], buf[i])
            i = i + 1

    def test_ValueAverage(self):
        sample = self.Sensor.Read()
        avg = self.Sensor.ValueAverage

        self.assertEqual(avg, sample)
