import logging
import pygetwindow as gw

from game.screenInfo import ScreenInfo
from properties.config import DPI_SCALING

logger = logging.getLogger('WindowManager')


class WindowManager:
    _screen_info = ScreenInfo(1920, 1080)

    @classmethod
    def getWindowSize(cls):
        try:
            window = gw.getActiveWindow()
            if window is None:
                raise ValueError("No active window found.")
            cls._screen_info = ScreenInfo(
                int(window.width / DPI_SCALING),
                int(window.height / DPI_SCALING)
            )
            return cls._screen_info
        except Exception as e:
            logger.error(f"Error getting window size: {e}")
            return cls._screen_info

    @classmethod
    def getScreenInfo(cls):
        cls.getWindowSize()
        return cls._screen_info