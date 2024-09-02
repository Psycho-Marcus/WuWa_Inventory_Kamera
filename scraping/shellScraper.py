import mss
import cv2
import logging
import pytesseract
import numpy as np

logger = logging.getLogger('ShellScraper')

def getShell(WIDTH, HEIGHT):
	xShell, yShell, wShell, hShell = (
		int(1255 / 1920 * WIDTH),
		int(45 / 1080 * HEIGHT),
		int(140 / 1920 * WIDTH),
		int(35 / 1080 * HEIGHT)
	)

	with mss.mss() as sct:
		image = np.array(sct.grab((0, 0, WIDTH, HEIGHT)))
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


	try: shell = int(pytesseract.image_to_string(image[yShell:yShell+hShell, xShell:xShell+wShell], config='outputbase digits').strip())
	except: 
		logger.critical("Failed to get shells. Error: ", exc_info=True)
		shell = 0

	return {'2': shell}