import sys
sys.path.append('../src/')

import unittest

from stubs import TestObserver
from middleware.SubjectObserver.SubjectObserver import Observer
from middleware.SubjectObserver.SubjectObserver import Subject

class TestSubjectObserver(unittest.TestCase):

	
	def setUp(arg):
		TestSubjectObserver.Subject = Subject()
		
		
	def tearDown(arg):
		return
	
	def testAttach(self):
		observer = TestObserver.TestObserver()
		self.Subject.Attach(observer)
		
		self.assertEqual(len(self.Subject._Observers), 1)
		self.assertEqual(observer._Subject, self.Subject)
		self.assertEqual(observer.Subject(), self.Subject)
		
	def testDetach(self):
		observer = TestObserver.TestObserver()
		self.Subject.Attach(observer)
		
		self.Subject.Detach(observer)
		
		self.assertEqual(len(self.Subject._Observers), 0)
		self.assertEqual(observer._Subject, None)
		self.assertEqual(observer.Subject(), None)
		
	def testSetStateNoObservers(self):
		value = 4
		self.Subject.State = value
		
		self.assertTrue(self.Subject._State, value)
		
	def testSetStateWithObservers(self):
		value = 4
		
		observer = TestObserver.TestObserver()
		self.Subject.Attach(observer)
		self.Subject.State = value

		self.assertEqual(observer.State, value)
		
	def testGetState(self):
		value = 4
		self.Subject.State = value
		
		self.assertEqual(self.Subject.State, value)



