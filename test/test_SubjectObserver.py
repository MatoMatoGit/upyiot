import sys
sys.path.append('../src/')

# Test libraries
import unittest
from stubs import TestObserver

# Unit Under Test
from middleware.SubjectObserver.SubjectObserver import Observer
from middleware.SubjectObserver.SubjectObserver import Subject

class test_SubjectObserver(unittest.TestCase):

	
	def setUp(arg):
		test_SubjectObserver.Subject = Subject()
		
		
	def tearDown(arg):
		return
	
	def test_Attach(self):
		observer = TestObserver.TestObserver()
		self.Subject.Attach(observer)
		
		self.assertEqual(len(self.Subject._Observers), 1)
		self.assertEqual(observer._Subject, self.Subject)
		self.assertEqual(observer.Subject(), self.Subject)
		
	def test_Detach(self):
		observer = TestObserver.TestObserver()
		self.Subject.Attach(observer)
		
		self.Subject.Detach(observer)
		
		self.assertEqual(len(self.Subject._Observers), 0)
		self.assertEqual(observer._Subject, None)
		self.assertEqual(observer.Subject(), None)
		
	def test_SetStateNoObservers(self):
		value = 4
		self.Subject.State = value
		
		self.assertTrue(self.Subject._State, value)
		
	def test_SetStateWithObservers(self):
		value = 4
		
		observer = TestObserver.TestObserver()
		self.Subject.Attach(observer)
		self.Subject.State = value

		self.assertEqual(observer.State, value)
		
	def test_GetState(self):
		value = 4
		self.Subject.State = value
		
		self.assertEqual(self.Subject.State, value)
		
	def test_ObserverCount(self):
		observer = TestObserver.TestObserver()
		self.Subject.Attach(observer)
		
		self.assertEqual(self.Subject.ObserverCount, 1)


