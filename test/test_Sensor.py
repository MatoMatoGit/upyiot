import sys
sys.path.append('../')

# Test libraries
import unittest
from stubs import TestObserver
from upyiot.drivers.Sensors.DummySensor import DummySensor

# Unit Under Test
from upyiot.middleware.Sensor import Sensor

# Other
from upyiot.middleware.AvgFilter import AvgFilter


class test_Sensor(unittest.TestCase):

    TestDir = "./"
    Name = "dummy"
    Sensor = None
    Samples = [20, 21, 25, 30, 35, 35, 20, 12, 10, 40]
    FilterDepth = 3

    def setUp(arg):
        test_Sensor.Dummy = DummySensor(test_Sensor.Samples)
        test_Sensor.Sensor = Sensor.Sensor(test_Sensor.TestDir,
                                           test_Sensor.Name,
                                           test_Sensor.FilterDepth, test_Sensor.Dummy,
                                           samples_per_update=1)
        test_Sensor.Filter = AvgFilter.AvgFilter(test_Sensor.FilterDepth)
        return

    def tearDown(arg):
        test_Sensor.Sensor.SamplesDelete()
        return

    def GetFiltered(self, filter, start_index):
        print(start_index)
        j = start_index
        for i in range(0, filter.Depth):
            print(i)
            print(j)
            filter.Input(self.Samples[j])
            if j < (len(self.Samples) - 1):
                j += 1
            else:
                j = 0

        return filter.Output(), j

    def test_Read(self):
        sample = self.Sensor.Read()

        print(sample)
        self.assertEqual(sample, self.GetFiltered(self.Filter, 0)[0])

    def test_NewSampleObserverSingleSample(self):
        sample_observer = TestObserver.TestObserver()

        self.Sensor.ObserverAttachNewSample(sample_observer)
        sample = self.Sensor.Read()

        print(sample_observer.State)
        print(sample)
        self.assertEqual(sample_observer.State, sample)
        self.assertEqual(sample_observer.UpdateCount, 1)

    def test_NewSampleObserverMultipleSamples(self):
        num_samples = int(len(self.Samples) / 2)
        samples = list()

        sensor = Sensor.Sensor(test_Sensor.TestDir,
                               test_Sensor.Name + "1",
                               test_Sensor.FilterDepth,
                               test_Sensor.Dummy,
                               samples_per_update=num_samples)

        sample_observer = TestObserver.TestObserver()

        sensor.ObserverAttachNewSample(sample_observer)

        start = 0
        for i in range(0, len(self.Samples)):
            samples.append(sensor.Read())
            i += 1
            print(samples, i, num_samples, i-start)

            if i-start is num_samples:
                print("COMPARE")
                for s in samples:
                    print(s)
                    c = sample_observer.State.pop(0)
                    print(c)
                    self.assertEqual(s, c)
                samples.clear()
                start = i

        sensor.SamplesDelete()
        print(sample_observer.UpdateCount, int(len(self.Samples) / num_samples))
        self.assertEqual(sample_observer.UpdateCount, int(len(self.Samples) / num_samples))

    def test_SamplesGet(self):
        filtered = list()
        sample_index = 0
        for i in range(0, len(self.Samples)):
            sample = self.Sensor.Read()
            filtered_sample, sample_index = self.GetFiltered(self.Filter, sample_index)
            filtered.append(filtered_sample)
            self.assertEqual(filtered_sample, sample)

        cnt, buf = self.Sensor.SamplesGet()
        print(cnt, buf)
        self.assertEqual(cnt, len(self.Samples))
        self.assertEqual(self.Sensor.SamplesCount, 0)

        for i in range(0, cnt):
            self.assertEqual(filtered[i], buf[i])
            i += 1

    def test_ValueAverage(self):
        sample = self.Sensor.Read()
        avg = self.Sensor.ValueAverage

        self.assertEqual(avg, sample)
