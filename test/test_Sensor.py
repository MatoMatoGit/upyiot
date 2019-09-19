import sys
sys.path.append('../src/')

import unittest

from stubs import TestObserver
from stubs import DummySensor
from middleware.Sensor import Sensor
from middleware.AvgFilter import AvgFilter

class TestSensor(unittest.TestCase):
	
	TestDir = "./"
	Name = "dummy"
	Sensor = None
	Samples = [20, 21, 25, 30, 35, 35, 20, 12, 10, 40]
	
	def setUp(arg):
		filter_depth = len(TestSensor.Samples)
		dummy = DummySensor.DummySensor(TestSensor.Samples)
		TestSensor.Sensor = Sensor.Sensor(TestSensor.TestDir, 
										TestSensor.Name,
										filter_depth, dummy)
		TestSensor.Filter = AvgFilter.AvgFilter(filter_depth)
		return
		
		
	def tearDown(arg):
		TestSensor.Sensor.SamplesDelete()
		return
	
	def testRead(self):
		sample = self.Sensor.Read()
		
		self.assertEqual(sample, self.Samples[0])
		
	def testNewSampleObserver(self):
		sample_observer = TestObserver.TestObserver()
		
		self.Sensor.ObserverAttachNewSample(sample_observer)
		sample = self.Sensor.Read()
		
		self.assertEqual(sample_observer.State, sample)
		
	
	def testSamplesGet(self):
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
		