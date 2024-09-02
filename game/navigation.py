import ctypes
import os
import pygetwindow as gw
import logging

logger = logging.getLogger('ProcessUtils')

# Constants
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
MAX_PATH = 260

# Define ctypes functions
user32 = ctypes.WinDLL('user32')
kernel32 = ctypes.WinDLL('kernel32')

class ProcessUtils:
	"""Handles operations related to process and window information."""

	def __init__(self):
		self.process_query_info = PROCESS_QUERY_LIMITED_INFORMATION

	def getPID(self, window_handle) -> int:
		"""
		Retrieve the process ID associated with the given window handle.

		Args:
			window_handle (int): Handle to the window.

		Returns:
			int: Process ID of the window.
		"""
		process_id = ctypes.c_ulong()
		user32.GetWindowThreadProcessId(window_handle, ctypes.byref(process_id))
		return process_id.value

	def getPPATH(self, process_id) -> str:
		"""
		Retrieve the executable path of the process given its ID.

		Args:
			process_id (int): Process ID of the target process.

		Returns:
			str: Full path to the executable, or None if unable to retrieve.
		"""
		process_handle = kernel32.OpenProcess(self.process_query_info, False, process_id)
		if not process_handle:
			logger.error(f"Failed to open process with ID: {process_id}")
			return None

		path_buffer = ctypes.create_string_buffer(MAX_PATH)
		if kernel32.QueryFullProcessImageNameA(process_handle, 0, path_buffer, ctypes.byref(ctypes.c_uint(MAX_PATH))):
			path = path_buffer.value.decode('utf-8')
			kernel32.CloseHandle(process_handle)
			return path
		else:
			logger.error(f"Failed to retrieve process path for ID: {process_id}")
			kernel32.CloseHandle(process_handle)
			return None

	def getPNAME(self, path) -> str:
		"""
		Extract the process name from its executable path.

		Args:
			path (str): Full path to the executable.

		Returns:
			str: Process name extracted from the path.
		"""
		process_name = os.path.basename(path)
		return process_name

	def getWindowByTitle(self, title) -> list:
		"""
		Retrieve all windows with the specified title.

		Args:
			title (str): Title of the window to match.

		Returns:
			list: List of windows matching the title.
		"""
		windows = gw.getWindowsWithTitle(title)
		return windows
