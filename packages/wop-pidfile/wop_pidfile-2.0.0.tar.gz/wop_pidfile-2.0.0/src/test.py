import os
import unittest
from wop_pidfile import PidFile

class TestPidFile(unittest.TestCase):
	def test_smartpointer(self):
		def only_in_here_is_pidfile_existing():
			pidfile = PidFile("testpidfile.pid", True)
			self.assertTrue(os.path.exists("testpidfile.pid"))
		only_in_here_is_pidfile_existing()
		self.assertFalse(os.path.exists("testpidfile.pid"))

if __name__ == '__main__':
	unittest.main()