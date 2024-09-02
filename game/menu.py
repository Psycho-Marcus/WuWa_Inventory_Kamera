import numpy as np
import mss
import time
import logging
import cv2
import pytesseract

import properties.config
from game.screenSize import WindowManager
from game.foreground import WindowFocusManager
from scraping.utils import pressEscape

logger = logging.getLogger('MainMenuController')

class MainMenuController:
    """Handles interactions with the screen and performs actions based on visual content."""

    def isMenu(self) -> bool:
        """
        Checks if the current screen shows the main menu.

        Returns:
            bool: True if the main menu is detected, False otherwise.
        """
        screenshot_region = {
            'left': int(140 / 1920 * WindowManager.getWidth()),
            'top': int(45 / 1080 * WindowManager.getHeight()),
            'width': int(140 / 1920 * WindowManager.getWidth()),
            'height': int(30 / 1080 * WindowManager.getHeight())
        }

        try:
            with mss.mss() as sct:
                screenshot = np.array(sct.grab(screenshot_region), dtype=np.uint8)
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

            result = pytesseract.image_to_string(screenshot).strip().lower()
            logger.debug(f"Detected text from screenshot: '{result}'")
            
            return result in ['terminal', 'terminat']
        except Exception as e:
            logger.error(f"Failed to capture or process screenshot: {e}")
            return False

    def isInMainMenu(self):
        """
        Checks if the application is in the main menu and handles errors if not.

        Returns:
            tuple: A tuple of three elements:
                - Status code (str): Empty string on success, 'error' on failure.
                - Status message (str): Descriptive message based on the result.
                - Additional information (str): Empty string on success, error message on failure.
        """
        try:
            result = WindowFocusManager().setForeground()
            if result[0] == 'error':
                return result
            time.sleep(0.2)
            WindowManager.updateWindowSize()

            time.sleep(1)

            if not self.isMenu():
                return 'error', 'Error', 'Not in the main menu. Press ESC in-game and rerun the scanner.'

            pressEscape()
            return '', '', ''

        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            return 'error', 'Exception', str(e)
