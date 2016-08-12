from zephyr.__main__ import Toolkit

class TestToolkit(Toolkit):
	"""
	Use this trivial subclass so Cement doesn't look at the environment.
	"""
	class Meta:
		argv = []
		config_files = []