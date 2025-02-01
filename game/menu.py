import time
import logging
from difflib import get_close_matches as getMatches

from game.foreground import WindowManager
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
            screenInfo = WindowManager().getScreenInfo()
            image = screenshot(
                screenInfo.terminal.x,
                screenInfo.terminal.y,
                screenInfo.terminal.w,
                screenInfo.terminal.h,
                screenInfo.monitor
            )

            result = imageToString(image, '').lower()
            logger.debug(f"Detected text from screenshot: '{result}'")
            
            return 'terminal' if getMatches(result, [definedText['PrefabTextItem_1547656443_Text']]) else False # MULTILANG
        except Exception as e:
            logger.error(f"Failed to capture or process screenshot: {e}", exc_info=True)
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
            result = WindowManager().setForeground()
            if result[0] == 'error':
                return result
            time.sleep(.2)

            if not self.isMenu():
                return 'error', 'Error', 'Not in the main menu. Press ESC in-game and rerun the scanner.'

            return '', '', ''

        except Exception as e:
            logger.error(f"Exception occurred: {e}", exc_info=True)
            return 'error', 'Exception', str(e)
