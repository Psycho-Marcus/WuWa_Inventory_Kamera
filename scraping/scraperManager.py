import os
import sys
import time
import signal
import logging
import multiprocessing
from datetime import datetime

from properties.config import FAILED, INVENTORY
from scraping.utils import (
	savingScraped, scaleWidth, scaleHeight,
    presskey
)

from scraping.shellScraper import getShell
from scraping.itemsScraper import itemsScraper
from scraping.charactersScraper import resonatorScraper
from scraping.weaponsScraper import weaponScraper
from scraping.echoesScraper import echoScraper
from scraping.achievementsScraper import achievementScraper

from game.menu import MainMenuController
from game.screenSize import WindowManager
from game.isForeground import isGameForeground
from game.foreground import WindowFocusManager
from game.stopKey import KeyPressChecker

logger = logging.getLogger('ScraperManager')

def managerStart(scraperEnabled: list):
	global INVENTORY, FAILED
	INVENTORY['date'] = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

	result = MainMenuController().isInMainMenu()
	if result[0] == 'error':
		return result
	time.sleep(1.2)

	WIDTH, HEIGHT = WindowManager.getWidth(), WindowManager.getHeight()

	completeFLAG = multiprocessing.Event()
	queue = multiprocessing.Queue()
	
	scrapersProcess = multiprocessing.Process(target=scrapers, args=(scraperEnabled, WIDTH, HEIGHT, completeFLAG, queue, INVENTORY['date']))
	scrapersProcess.start()

	stopMonitor = multiprocessing.Process(target=needToStop, args=(scrapersProcess.pid, completeFLAG, WindowFocusManager.getGamePID()))
	stopMonitor.start()

	scrapersProcess.join()
	
	stopMonitor.terminate()
	stopMonitor.join()

	while not queue.empty():
		scraperResult = queue.get()
		INVENTORY['items'].update(scraperResult['inventory'])
		FAILED.extend(scraperResult['failed'])
	savingScraped(START_DATE=INVENTORY['date'])

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

def scrapers(scraperEnabled: list, WIDTH: int, HEIGHT: int, FLAG: multiprocessing.Event, queue: multiprocessing.Queue, START_DATE: str): # type: ignore
	resonator = dict()
	inventory = dict()
	failed = list()
	weapons = list()
	echoes = list()
	achievements = list()

	for scraper in scraperEnabled:
		presskey('esc', .5)

		match(scraper):
			case 'characters':
				resonator = resonatorScraper(WIDTH, HEIGHT)
			case 'weapons':
				i, w = weaponScraper(scaleWidth(81.5, WIDTH), scaleHeight(191.5, HEIGHT), WIDTH, HEIGHT)
				inventory.update(i)
				weapons.extend(w)
			case 'echoes':
				echoes = echoScraper(scaleWidth(81.5, WIDTH), scaleHeight(326.5, HEIGHT), WIDTH, HEIGHT)
			case 'devItems':
				i, f = itemsScraper(START_DATE, scaleWidth(81.5, WIDTH), scaleHeight(596.5, HEIGHT), WIDTH, HEIGHT)
				inventory.update(i)
				failed.extend(f)
			case 'resources':
				i, f = itemsScraper(START_DATE, scaleWidth(81.5, WIDTH), scaleHeight(731.5, HEIGHT), WIDTH, HEIGHT)
				inventory.update(i)
				failed.extend(f)
			case 'achievements':
				achievements = achievementScraper(WIDTH, HEIGHT)

		if scraper not in ['characters', 'achievements']:
			if '2' not in inventory or inventory.get('2') == 0:
				shell = getShell(WIDTH, HEIGHT)
				inventory = {**shell, **inventory}

	presskey('esc')
	FLAG.set()

	savingScraped({
			'characters_wuwainventorykamera.json': (resonator, dict),
			'weapons_wuwainventorykamera.json': (weapons, list),
			'echoes_wuwainventorykamera.json': (echoes, list),
			'achievements_wuwainventorykamera.json': (achievements, list),
		}, START_DATE
	)

	queue.put({'inventory': inventory, 'failed': failed})
