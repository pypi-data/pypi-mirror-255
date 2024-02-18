import os
import signal

class PidFile():
	"""Use this class as a smart pointer in your main function to create a pidfile.
	The pidfile is removed when the object is deleted.

	Example usage:
	if __name__ == "__main__":
		pidfile = PidFile("my_program.pid", True)
		# Your code here
	"""
	def __init__(self, filename="pidfile.pid", killOldProcess=True):
		self.filename = filename
		self.killOldProcess = killOldProcess
		self.__createPidFile(self.filename, self.killOldProcess)

	def __del__(self):
		"""Removes the pidfile when the object is deleted.
		This happens when the program ends or the object is deleted manually.
		"""
		os.remove(self.filename)

	def __createPidFile(self, filename, killOldProcess):
		"""Writes the process ID of the running Python process to the PID-file. If a pidfile exists it kills the running process if wanted.
		:param filename: The name of the PID-File. 'pidfile.pid' by default.
		:param killOldProcess: Stops the process with the process ID found in the pidfile. True by default.
		"""
		if killOldProcess:
			try:
				with open(filename, "r") as pidfile:
					pid = pidfile.read()
					os.kill(int(pid), signal.SIGTERM)
			except FileNotFoundError:
				pass
			except PermissionError:
				pass
			except OSError:
				pass
			except ValueError:
				pass
		with open(filename, "w") as pidfile:
			pidfile.write(str(os.getpid()))
