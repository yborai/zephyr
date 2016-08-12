import unittest
from cement.utils import test
from . import TestToolkit

class TestZephyrCLI(test.CementTestCase):
	app_class = TestToolkit

	def setUp(self):
		super(TestZephyrCLI, self).setUp()
		self.reset_backend()
		self.app = TestToolkit(argv=[], config_files=[])
		self.app.setup()
		print("Testing Zephyr")

	def test_zephyr(self):
		print ("Testing 'Zephyr' call")
		with self.assertRaises(SystemExit) as cm:
			self.app.run()
			self.eq(cm.exception.code, 0)
		