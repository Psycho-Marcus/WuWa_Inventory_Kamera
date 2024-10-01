import logging
import string

from scraping.utils import (
	scaleWidth, scaleHeight, screenshot,
	imageToString
)

logger = logging.getLogger('ShellScraper')

def getShell(WIDTH, HEIGHT):

	xShell, yShell, wShell, hShell = (
		scaleWidth(1255, WIDTH),
		scaleHeight(38, HEIGHT),
		scaleWidth(165, WIDTH),
		scaleHeight(50, HEIGHT)
	)

	image = screenshot(xShell, yShell, wShell, hShell, True)

	try: shell = int(imageToString(image, allowedChars=string.digits).strip())
	except Exception as e:
		logger.debug(f'Failed to get shells. Error: {e}', exc_info=True)
		shell = 0

	return {'2': shell}