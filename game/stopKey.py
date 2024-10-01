import ctypes
import ctypes.wintypes as wintypes
import logging

logger = logging.getLogger('KeyPressChecker')

# Constants
VIRTUAL_KEY_ENTER = 0x0D

class KeyPressChecker:
	"""Encapsulates functionality to check the state of a specific virtual key."""

	def __init__(self):
		try:
			# Load user32 DLL
			self.user32 = ctypes.WinDLL('user32', use_last_error=True)
			# Define API function
			self.GetAsyncKeyState = self.user32.GetAsyncKeyState
			self.GetAsyncKeyState.restype = wintypes.SHORT
			self.GetAsyncKeyState.argtypes = [wintypes.INT]
		except Exception as e:
			logger.error(f"Failed to initialize KeyPressChecker: {e}")
			raise

	def isPressed(self):
		"""
		Checks if the specified virtual key is currently pressed.

		Args:
			virtual_key_code (int): The virtual key code to check.

		Returns:
			bool: True if the key is pressed, False otherwise.
		"""
		try:
			key_state = self.GetAsyncKeyState(VIRTUAL_KEY_ENTER)
			pressed = (key_state & 0x8000) != 0

			return pressed
		except Exception as e:
			logger.error(f"Error checking key press state: {e}")
			return False