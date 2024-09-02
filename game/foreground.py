import ctypes
import logging

from game.navigation import ProcessUtils
from properties.config import PROCESS_NAME, WINDOW_NAME

logger = logging.getLogger('WindowFocusManager')

# Constants
SW_RESTORE = 9
HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0004

class WindowFocusManager:
	"""Handles operations to bring a window to the foreground and set its properties."""
	
	PROCESS_ID = None

	def __init__(self):
		self.process_utils = ProcessUtils()

	@classmethod
	def setGamePID(cls, pID):
		"""Class method to retrieve the PROCESS_ID."""
		cls.PROCESS_ID = pID

	@classmethod
	def getGamePID(cls):
		"""Class method to retrieve the PROCESS_ID."""
		return cls.PROCESS_ID

	def _setForeground(self, hwnd):
		"""Restore, bring to foreground, and set the window as topmost."""
		ctypes.windll.user32.ShowWindow(hwnd, SW_RESTORE)
		ctypes.windll.user32.SetForegroundWindow(hwnd)
		ctypes.windll.user32.SetWindowPos(
			hwnd, HWND_TOPMOST, 0, 0, 0, 0,
			SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE
		)

	def setForeground(self):
		"""Find window by title and focus it if its process matches the given process name."""
		try:
			matching_windows = self.process_utils.getWindowByTitle(WINDOW_NAME)
			
			logger.debug(f"Looking for windows with title '{WINDOW_NAME}'")
			logger.debug(f"Found {len(matching_windows)} matching windows")

			if not matching_windows:
				logger.warning(f"No window found with title '{WINDOW_NAME}'")
				return 'error', 'No window found', 'No window with the specified title was found.'

			for win in matching_windows:
				hwnd = win._hWnd
				pID = self.process_utils.getPID(hwnd)
				pPATH = self.process_utils.getPPATH(pID)
				pName = self.process_utils.getPNAME(pPATH) if pPATH else None

				logger.debug(f"Window handle: {hwnd}, PID: {pID}, Path: {pPATH}, Name: {pName}")

				if pName == PROCESS_NAME:
					WindowFocusManager.PROCESS_ID = pID
					logger.info(f"Found matching process. Set PROCESS_ID to {pID}.")
					self._setForeground(hwnd)
					return '', '', ''
				else:
					logger.debug(f"Process name '{pName}' does not match expected '{PROCESS_NAME}'")

			logger.warning(f"No window found with process name '{PROCESS_NAME}'")
			return 'error', 'Window not found', 'Window with the specified process name not found.'

		except Exception as e:
			logger.error(f"Exception occurred in setForeground: {str(e)}", exc_info=True)
			return 'error', 'Exception occurred', str(e)