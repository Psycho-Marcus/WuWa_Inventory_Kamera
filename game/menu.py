import time
import logging
from difflib import get_close_matches

from game.screenSize import WindowManager
from game.foreground import WindowFocusManager
from scraping.utils.common import definedText
from scraping.utils import (
    screenshot, imageToString
)

logger = logging.getLogger('MainMenuController')

class MainMenuController:
    """Handles interactions with the screen and performs actions based on visual content."""

    def isMenu(self) -> bool:
        """
        Checks if the current screen shows the main menu.

        Returns:
            bool: True if the main menu is detected, False otherwise.
        """
        try:
            screenInfo = WindowManager.getScreenInfo()
            image = screenshot(
                screenInfo.scaleWidth((140, 132)),
                screenInfo.scaleHeight((40, 32)),
                screenInfo.scaleWidth(150),
                screenInfo.scaleHeight(40)
            )

            result = imageToString(image, '').lower()
            logger.debug(f"Detected text from screenshot: '{result}'")
            
            return  'terminal' if get_close_matches(result, [definedText['PrefabTextItem_1547656443_Text']]) else 'none' # MULTILANG
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
            time.sleep(.2)

            if not self.isMenu():
                return 'error', 'Error', 'Not in the main menu. Press ESC in-game and rerun the scanner.'

            return '', '', ''

        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            return 'error', 'Exception', str(e)
