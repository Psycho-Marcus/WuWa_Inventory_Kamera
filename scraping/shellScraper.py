import logging
import string

from scraping.utils import (
	screenshot, imageToString
)
from game.screenInfo import ScreenInfo

logger = logging.getLogger('ShellScraper')

def getShell(screenInfo: ScreenInfo):
	xShell, yShell, wShell, hShell = (
		screenInfo.scaleWidth((1255, 1100)),
		screenInfo.scaleHeight((38, 35)),
		screenInfo.scaleWidth((165, 145)),
		screenInfo.scaleHeight((50, 40))
	)

	image = screenshot(xShell, yShell, wShell, hShell, True)

	try: shell = int(imageToString(image, allowedChars=string.digits).strip())
	except Exception as e:
		logger.debug(f'Failed to get shells. Error: {e}', exc_info=True)
		shell = 0

	return {'2': shell}