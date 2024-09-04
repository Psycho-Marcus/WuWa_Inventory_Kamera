import logging
import string
import pytesseract

from scraping.utils import (
	scaleWidth, scaleHeight, screenshot,
	convertToBlackWhite
)

logger = logging.getLogger('ShellScraper')

def getShell(WIDTH, HEIGHT):

	xShell, yShell, wShell, hShell = (
		scaleWidth(1255, WIDTH),
		scaleHeight(45, HEIGHT),
		scaleWidth(145, WIDTH),
		scaleHeight(35, HEIGHT)
	)

	image = screenshot(0, 0, WIDTH, HEIGHT)
	bw = convertToBlackWhite(image[yShell:yShell+hShell, xShell:xShell+wShell])

	try: shell = int(pytesseract.image_to_string(bw, config=f'--psm 7 -c tessedit_char_whitelist={string.digits}').strip())
	except: 
		logger.debug("Failed to get shells. Error: ", exc_info=True)
		shell = 0

	return {'2': shell}