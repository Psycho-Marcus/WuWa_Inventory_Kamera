import logging
import pygetwindow as gw

from properties.config import DPI_SCALING

logger = logging.getLogger('WindowManager')

class WindowManager:
	_width = 1920
	_height = 1080

	@classmethod
	def getWindowSize(cls):
		"""Update and return the size of the active window, adjusted for DPI scaling."""
		try:
			window = gw.getActiveWindow()
			if window is None:
				raise ValueError("No active window found.")
			cls._width = int(window.width / DPI_SCALING)
			cls._height = int(window.height / DPI_SCALING)
			return cls._width, cls._height
		except Exception as e:
			logger.error(f"Error getting window size: {e}")
			return cls._width, cls._height

	@classmethod
	def getWidth(cls):
		"""Return the width of the active window."""
		return cls._width

	@classmethod
	def getHeight(cls):
		"""Return the height of the active window."""
		return cls._height

	@classmethod
	def updateWindowSize(cls):
		"""Update the stored window size."""
		cls.getWindowSize()
