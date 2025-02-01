import win32api
import logging

logger = logging.getLogger('KeyPressChecker')

# Constants
VIRTUAL_KEY_ENTER = 0x0D

class KeyPressChecker:
	"""Encapsulates functionality to check the state of a specific virtual key."""

	def isPressed(self):
		"""
		Checks if the specified virtual key is currently pressed.

		Returns:
			bool: True if the key is pressed, False otherwise.
		"""
		try:
			keyState = win32api.GetAsyncKeyState(VIRTUAL_KEY_ENTER)
			pressed = (keyState & 0x8000) != 0

			return pressed
		except Exception as e:
			logger.error(f"Error checking key press state: {e}", exc_info=True)
			return False