import os
import sys
import time
import signal
import logging
import multiprocessing

from properties.config import FAILED, INVENTORY, CHARACTERS
from scraping.utils import (
	pressEscape, savingScraped, scaleWidth,
	scaleHeight
)
from scraping.itemsScraper import itemsScraper
from scraping.charactersScraper import resonatorScraper
from scraping.shellScraper import getShell
from game.menu import MainMenuController
from game.screenSize import WindowManager
from game.isForeground import isGameForeground
from game.foreground import WindowFocusManager
from game.stopKey import KeyPressChecker

logger = logging.getLogger('ScraperManager')

def managerStart(scraperEnabled: list):
	global FAILED, INVENTORY

	result = MainMenuController().isInMainMenu()
	if result[0] == 'error':
		return result
	time.sleep(2)

	WIDTH, HEIGHT = WindowManager.getWidth(), WindowManager.getHeight()

	completeFLAG = multiprocessing.Event()
	queue = multiprocessing.Queue()
	
	scrapersProcess = multiprocessing.Process(target=scrapers, args=(scraperEnabled, WIDTH, HEIGHT, completeFLAG, queue))
	scrapersProcess.start()

	stopMonitor = multiprocessing.Process(target=needToStop, args=(scrapersProcess.pid, completeFLAG, WindowFocusManager.getGamePID()))
	stopMonitor.start()

	scrapersProcess.join()
	
	stopMonitor.terminate()
	stopMonitor.join()

	while not queue.empty():
		scraperResult = queue.get()
		INVENTORY.update(scraperResult['inventory'])
		FAILED += scraperResult['failed']
		CHARACTERS.update(scraperResult['characters'])

	savingScraped()

	if len(FAILED) > 0:
		return ('failed', 'Failed to recognize', f'Failed to recognize {len(FAILED)} items.')
	else:
		return ('success', 'Complete', f'Scan completed with no errors.')


def needToStop(tPID, completeFLAG, PROCESS_ID):
	keyPress = KeyPressChecker()

	while not completeFLAG.is_set():
		# Check if the game is no longer in the foreground or if the key is pressed
		if not isGameForeground().isForeground(PROCESS_ID) or keyPress.isPressed():
			try:
				os.kill(tPID, signal.SIGTERM)
				logger.debug("Terminated scraper process due to key press or game not in foreground.")
			except Exception as e:
				logger.error(f"Error terminating process: {e}")
			sys.exit(0)
		time.sleep(.1)

def scrapers(scraperEnabled: list, WIDTH: int, HEIGHT: int, FLAG: multiprocessing.Event, queue: multiprocessing.Queue): # type: ignore
	resonator = dict()
	inventory = dict()
	failed = list()

	for scraper in scraperEnabled:
		match(scraper):
			case 'characters':
				resonator = resonatorScraper(WIDTH, HEIGHT)
			case 'weapons': pass
			case 'echoes': pass
			case 'devItems':
				i, f = itemsScraper(scaleWidth(81.5, WIDTH), scaleHeight(596.5, HEIGHT), WIDTH, HEIGHT)
				inventory.update(i)
				failed += f
			case 'resources':
				i, f = itemsScraper(scaleWidth(81.5, WIDTH), scaleHeight(731.5, HEIGHT), WIDTH, HEIGHT)
				inventory.update(i)
				failed += f
		

		if scraper in ['devItems', 'resources']:
			if '2' not in inventory or inventory.get('2') == 0:
				shell = getShell(WIDTH, HEIGHT)
				inventory = {**shell, **inventory}
				


		pressEscape()
		time.sleep(.5)
	FLAG.set()

	queue.put({'inventory': inventory, 'failed': failed, 'characters': resonator})
